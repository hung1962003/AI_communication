import { useState, useCallback } from "react";
import PropTypes from "prop-types";
import { LiveKitRoom, RoomAudioRenderer } from "@livekit/components-react";
import "@livekit/components-styles";
import SimpleVoiceAssistant from "./SimpleVoiceAssistant";

const LiveKitModal = ({ setShowSupport }) => {
  const [isSubmittingName, setIsSubmittingName] = useState(true);
  const [name, setName] = useState("");
  const [token, setToken] = useState(null);
  const [serverUrl, setServerUrl] = useState(null);

  const getToken = useCallback(async (userName) => {
    try {
      console.log("run");
      const response = await fetch(
        // `http://127.0.0.1:8080/getToken?name=${encodeURIComponent(userName)}`
         `https://aicom.aespwithai.com/getToken?name=${encodeURIComponent(userName)}`
      );
      
      console.log("status", response.status, "url", response.url);
      
      const body = await response.clone().text();
      console.log("raw body", body);
      const contentType = response.headers.get("content-type") || "";
      const bodyText = await response.text();
      if (!response.ok) {
        console.error("Error response:", bodyText);
        throw new Error(`Failed to get token: ${response.status} ${bodyText}`);
      }
      if (!contentType.includes("application/json")) {
        console.error("Unexpected response:", bodyText);
        throw new Error("Failed to get token: unexpected response format");
      }
      const data = JSON.parse(bodyText);
      setToken(data.token);
      setServerUrl(data.url);
      setIsSubmittingName(false);
    } catch (error) {
      console.error(error);
      setIsSubmittingName(true); // Reset to show form again on error
    }
  }, []);

  const handleNameSubmit = (e) => {
    e.preventDefault();
    if (name.trim()) {
      getToken(name);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="support-room">
          {isSubmittingName ? (
            <form onSubmit={handleNameSubmit} className="name-form">
              <h2>Enter your name to connect with support</h2>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                required
              />
              <button type="submit">Connect</button>
              <button
                type="button"
                className="cancel-button"
                onClick={() => setShowSupport(false)}
              >
                Cancel
              </button>
            </form>
          ) : token ? (
            <LiveKitRoom
              serverUrl={serverUrl || import.meta.env.VITE_LIVEKIT_URL}
              token={token}
              connect={true}
              video={false}
              audio={true}
              onDisconnected={() => {
                setShowSupport(false);
                setIsSubmittingName(true);
                setToken(null);
                setServerUrl(null);
              window.location.href = "/summary";
              }}
            >
              <RoomAudioRenderer />
              <SimpleVoiceAssistant />
            </LiveKitRoom>
          ) : null}
        </div>
      </div>
    </div>
  );
};

LiveKitModal.propTypes = {
  setShowSupport: PropTypes.func.isRequired,
};

export default LiveKitModal;
