import React, { useState } from "react";

interface Props {
  onSubmit: (email: string) => void;
  initial?: string;
}

const EmailPrompt: React.FC<Props> = ({ onSubmit, initial = "" }) => {
  const [email, setEmail] = useState(initial);

  return (
    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
      <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="your.email@example.com" />
      <button onClick={() => onSubmit(email)}>Save</button>
    </div>
  );
};

export default EmailPrompt;
