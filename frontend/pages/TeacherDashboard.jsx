import { useState } from "react";
import QRCode from "react-qr-code";
import TeacherAttendanceView from "./TeacherAttendanceView";
import TeacherOverride from "./TeacherOverride";

function TeacherDashboard({ user, onLogout }) {
  const [attendanceActive, setAttendanceActive] = useState(false);
  const [qrValue, setQrValue] = useState("");
  const [selectedSubject, setSelectedSubject] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [loading, setLoading] = useState(false);
  const [showAttendanceView, setShowAttendanceView] = useState(false);
  const [showOverride, setShowOverride] = useState(false);
  const [currentSession, setCurrentSession] = useState(null);

  // ✅ Subjects mapped to each teacher
  const subjectsByTeacher = {
    T001: [
      "Software Engineering and Project Management",
      "Computer Networks",
      "Theory of Computation"
    ],
    T002: [
      "Web Technology Lab",
      "Artificial Intelligence",
      "Research Methodology and IPR"
    ]
  };

  // Pick subjects for current logged-in teacher
  const subjects = subjectsByTeacher[user.usn] || [];

  // Show attendance view page
  if (showAttendanceView && currentSession) {
    return (
      <TeacherAttendanceView
        session={currentSession}
        onBack={() => setShowAttendanceView(false)}
      />
    );
  }

  // 🟩 Start attendance session
  const handleStartAttendance = async () => {
    if (!selectedSubject) {
      alert("Please select a subject first!");
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem("token");

      const response = await fetch("http://localhost:5000/qr/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          subject: selectedSubject,
          teacher_id: user.name
        })
      });

      const data = await response.json();

      if (response.ok) {
        const qrData = {
          session_id: data.session_id,
          subject: selectedSubject,
          timestamp: Date.now()
        };

        setSessionId(data.session_id);
        setQrValue(JSON.stringify(qrData));
        setAttendanceActive(true);
        setCurrentSession({
          session_id: data.session_id,
          subject: selectedSubject,
          teacher_id: user.name
        });
        alert(`✅ Attendance started for ${selectedSubject}!`);
      } else {
        alert(data.message || "Failed to start attendance");
      }
    } catch (error) {
      console.error("Error starting attendance:", error);
      alert("Error connecting to server");
    } finally {
      setLoading(false);
    }
  };

  // 🟥 Stop attendance session
  const handleStopAttendance = async () => {
    try {
      const token = localStorage.getItem("token");

      const response = await fetch("http://localhost:5000/qr/stop", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          session_id: sessionId
        })
      });

      if (response.ok) {
        setAttendanceActive(false);
        setQrValue("");
        setSessionId("");
        setCurrentSession(null);
        alert("✅ Attendance stopped!");
      }
    } catch (error) {
      console.error("Error stopping attendance:", error);
    }
  };

  // 📋 View live attendance
  const handleViewAttendance = () => {
    if (currentSession) {
      setShowAttendanceView(true);
    }
  };

  // ✏️ Manual override handler
  const handleManualOverride = () => {
    setShowOverride(true);
  };

  // 🧱 UI
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Welcome, {user.name}!</h2>
        <button onClick={onLogout} className="btn-danger">Logout</button>
      </div>

      <div className="card">
        <h3>📊 Teacher Dashboard</h3>
        <p>Manage attendance for your classes</p>
      </div>

      <div className="attendance-section card">
        <h3>Start Attendance Session</h3>

        {!attendanceActive ? (
          <div className="subject-select">
            <label htmlFor="subject">Select Subject:</label>
            <select
              id="subject"
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              disabled={loading}
            >
              <option value="">-- Choose Subject --</option>
              {subjects.map((subject) => (
                <option key={subject} value={subject}>
                  {subject}
                </option>
              ))}
            </select>

            <button
              onClick={handleStartAttendance}
              disabled={loading || !selectedSubject}
              className="btn-success mt-2"
            >
              {loading ? "Starting..." : "🚀 Start Attendance"}
            </button>

            {/* Manual override button */}
            <button
              onClick={handleManualOverride}
              className="btn-warning mt-2"
              style={{ marginLeft: "10px" }}
            >
              ✏️ Manual Attendance Override
            </button>
          </div>
        ) : (
          <div className="qr-section">
            <h4>✅ Attendance Active for: {selectedSubject}</h4>
            <p className="info-message">
              Students can now scan this QR code to mark attendance
            </p>

            <div className="qr-display">
              <QRCode
                value={qrValue}
                size={256}
                style={{
                  margin: "20px auto",
                  display: "block",
                  border: "10px solid white",
                  boxShadow: "0 4px 12px rgba(0,0,0,0.15)"
                }}
              />
            </div>

            <div className="session-info">
              <p><strong>Session ID:</strong> {sessionId}</p>
              <p><strong>Subject:</strong> {selectedSubject}</p>
            </div>

            <div style={{ display: "flex", gap: "10px", marginTop: "20px" }}>
              <button
                onClick={handleViewAttendance}
                className="btn-success mt-3"
                style={{ flex: 1 }}
              >
                📋 View Live Attendance
              </button>

              <button
                onClick={handleStopAttendance}
                className="btn-danger mt-3"
                style={{ flex: 1 }}
              >
                ⏹️ Stop Attendance
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="card mt-3">
        <h3>📋 Quick Actions</h3>
        <button className="mt-2" disabled>View All Attendance Records</button>
        <button className="mt-2" disabled>Generate Reports</button>
      </div>

      {/* Show Manual Override Modal */}
      {showOverride && (
        <TeacherOverride
          teacher={user}
          onClose={() => setShowOverride(false)}
        />
      )}
    </div>
  );
}

export default TeacherDashboard;
