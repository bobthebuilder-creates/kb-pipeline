import React from "react";

interface Props {
  inputPath: string;
  onChange: (value: string) => void;
}

const InputPathPanel: React.FC<Props> = ({ inputPath, onChange }) => {
  return (
    <div style={{ border: "1px solid #444", borderRadius: 8, padding: 16, marginBottom: 16 }}>
      <h2>Input Path</h2>
      <p style={{ fontSize: 12 }}>
        Path inside the backend container (mapped from host). For Docker setup,
        anything under <code>/data/input</code> is valid, e.g. <code>/data/input/batch1</code>.
      </p>
      <input
        type="text"
        value={inputPath}
        onChange={(e) => onChange(e.target.value)}
        style={{ width: "100%" }}
        placeholder="/data/input/batch1"
      />
    </div>
  );
};

export default InputPathPanel;
