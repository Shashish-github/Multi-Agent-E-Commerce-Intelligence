"use client";

import { useEffect, useState } from "react";
import { Plus, Camera, Trash2, Play, Settings } from "lucide-react";
import { getCameras, createCamera, deleteCamera } from "@/lib/api";

interface Camera {
  id: string;
  name: string;
  source_type: string;
  source_reference: string;
  location_label: string | null;
  enabled: boolean;
  status: string;
}

export default function CamerasPage() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({
    name: "",
    source_type: "file",
    source_reference: "",
    location_label: "",
  });

  useEffect(() => {
    getCameras().then(setCameras).catch(console.error);
  }, []);

  const handleAdd = async () => {
    try {
      const camera = await createCamera({
        name: form.name,
        source_type: form.source_type,
        source_reference: form.source_reference,
        location_label: form.location_label || undefined,
      });
      setCameras([camera, ...cameras]);
      setShowAdd(false);
      setForm({ name: "", source_type: "file", source_reference: "", location_label: "" });
    } catch (error) {
      console.error("Failed to add camera:", error);
    }
  };

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Camera className="h-6 w-6" />
          Camera Management
        </h1>
        <button onClick={() => setShowAdd(!showAdd)} className="btn-primary flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add Camera
        </button>
      </div>

      {showAdd && (
        <div className="card mb-6">
          <div className="card-header">New Camera</div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              className="input-field"
              placeholder="Camera name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
            <select
              className="input-field"
              value={form.source_type}
              onChange={(e) => setForm({ ...form, source_type: e.target.value })}
            >
              <option value="file">Video File</option>
              <option value="rtsp">RTSP Stream</option>
              <option value="webcam">Webcam</option>
            </select>
            <input
              className="input-field"
              placeholder="Source path / URL / device index"
              value={form.source_reference}
              onChange={(e) => setForm({ ...form, source_reference: e.target.value })}
            />
            <input
              className="input-field"
              placeholder="Location label (optional)"
              value={form.location_label}
              onChange={(e) => setForm({ ...form, location_label: e.target.value })}
            />
          </div>
          <div className="flex gap-2 mt-4">
            <button onClick={handleAdd} className="btn-primary">Save</button>
            <button onClick={() => setShowAdd(false)} className="btn-primary bg-bg-tertiary text-text-secondary hover:bg-border">Cancel</button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {cameras.map((camera) => (
          <div key={camera.id} className="card">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Camera className="h-5 w-5 text-accent-blue" />
                <span className="font-medium">{camera.name}</span>
              </div>
              <span
                className={`badge ${
                  camera.status === "ONLINE" ? "badge-green" : "badge-red"
                }`}
              >
                {camera.status}
              </span>
            </div>
            <div className="text-sm text-text-secondary space-y-1">
              <div>Type: <span className="text-text-primary">{camera.source_type}</span></div>
              <div className="truncate">Source: <span className="text-text-primary font-mono text-xs">{camera.source_reference}</span></div>
              {camera.location_label && (
                <div>Location: <span className="text-text-primary">{camera.location_label}</span></div>
              )}
            </div>
            <div className="flex gap-2 mt-4">
              <a href={`/cameras/${camera.id}`} className="btn-primary text-xs flex items-center gap-1">
                <Play className="h-3 w-3" /> View
              </a>
              <button className="btn-primary text-xs flex items-center gap-1 bg-bg-tertiary">
                <Settings className="h-3 w-3" /> Configure
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
