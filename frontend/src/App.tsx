import React, { useState, useEffect } from "react";
import ChartDisplay from "./components/ChartDisplay";
import EditChartModal from "./components/EditChartModal";
import EmailPrompt from "./components/EmailPrompt";
import { DataPoint } from "./types/analytics";
import { supabase } from "./supabaseClient";

const DEFAULT_DATA: DataPoint[] = [
  { label: "Agent A", value: 120 },
  { label: "Agent B", value: 200 },
  { label: "Agent C", value: 95 },
  { label: "Agent D", value: 160 },
];

function App() {
  const [data, setData] = useState<DataPoint[]>(DEFAULT_DATA);
  const [editing, setEditing] = useState(false);
  const [email, setEmail] = useState<string | null>(null);
  const chartKey = "call_volume_1";

  // When user provides email we try to load their saved values
  useEffect(() => {
    if (!email) return;
    (async () => {
      const { data: rows, error } = await supabase
        .from("user_chart_values")
        .select("*")
        .eq("email", email)
        .eq("chart_key", chartKey)
        .single();
      if (error && error.code !== "PGRST116") {
        console.warn("supabase read error:", error);
      }
      if (rows && rows.values) {
        setData(rows.values);
      }
    })();
  }, [email]);

  const handleEdit = async () => {
    if (!email) {
      // alert for email
      const got = window.prompt("Please enter your email to save chart values:");
      if (!got) return;
      setEmail(got);
    }
    // If we have saved values, ask permission to overwrite
    if (email) {
      const { data: row } = await supabase
        .from("user_chart_values")
        .select("*")
        .eq("email", email)
        .eq("chart_key", chartKey)
        .single();
      if (row && row.values) {
        const ok = window.confirm("We found previous saved values. Overwrite them?");
        if (!ok) return;
      }
    }
    setEditing(true);
  };

  const saveValues = async (values: DataPoint[]) => {
    setData(values);
    setEditing(false);
    if (!email) {
      const got = window.prompt("Please enter your email to save chart values:");
      if (!got) return setEmail(got);
      setEmail(got);
    }
    // upsert into supabase
    const payload = {
      email,
      chart_key: chartKey,
      values,
      updated_at: new Date().toISOString(),
    };
    const { error } = await supabase.from("user_chart_values").upsert(payload, { onConflict: ["email", "chart_key"] });
    if (error) {
      console.warn("Failed to save to supabase:", error);
      alert("Failed to save values to remote. Values persisted locally in this session only.");
    } else {
      alert("Saved your custom values!");
    }
  };

  return (
    <div className="app">
      <div className="header">
        <div>
          <h1>Call Analytics Dashboard</h1>
          <div className="small">Voice agent analytics — Board</div>
        </div>
        <div>
          <button onClick={() => setData(DEFAULT_DATA)}>Reset</button>
          <button style={{ marginLeft: 8 }} onClick={handleEdit}>Edit Chart</button>
        </div>
      </div>

      <div className="card">
        <h2>Calls per Agent</h2>
        <ChartDisplay data={data} />
      </div>

      {editing && (
        <div className="card">
          <EditChartModal
            initial={data}
            onSave={(values) => saveValues(values)}
            onCancel={() => setEditing(false)}
          />
        </div>
      )}
    </div>
  );
}

export default App;
