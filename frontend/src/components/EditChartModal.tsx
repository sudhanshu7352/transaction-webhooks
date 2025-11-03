import React, { useState } from "react";
import { DataPoint } from "../types/analytics";

interface Props {
  initial: DataPoint[];
  onSave: (values: DataPoint[]) => void;
  onCancel: () => void;
}

const EditChartModal: React.FC<Props> = ({ initial, onSave, onCancel }) => {
  const [values, setValues] = useState(initial.map((d) => d.value.toString()));

  return (
    <div style={{ padding: 16 }}>
      <h3>Edit values</h3>
      <div>
        {initial.map((d, i) => (
          <div key={d.label} style={{ marginBottom: 8 }}>
            <label className="small">{d.label}</label>
            <input
              value={values[i]}
              onChange={(e) => {
                const copy = [...values];
                copy[i] = e.target.value;
                setValues(copy);
              }}
              style={{ marginLeft: 8 }}
            />
          </div>
        ))}
      </div>
      <div style={{ marginTop: 12 }}>
        <button onClick={() => onSave(initial.map((d, i) => ({ label: d.label, value: Number(values[i]) })))}>
          Save
        </button>
        <button className="secondary" style={{ marginLeft: 8 }} onClick={onCancel}>
          Cancel
        </button>
      </div>
    </div>
  );
};

export default EditChartModal;
