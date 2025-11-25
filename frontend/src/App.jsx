import { useState } from 'react'
import './App.css'
import LiveKitModal from './components/LiveKitModal';
import Feedback from './FeedbackAi.jsx';

function App() {
  const [showSupport, setShowSupport] = useState(false);
  const isSummaryPage = typeof window !== "undefined" && window.location.pathname === "/summary";

  if (isSummaryPage) {
    return <Feedback />;
  }

  const handleSupportClick = () => {
    setShowSupport(true)
  }

  return (
    <div className="app">
      

        <button className="support-button" onClick={handleSupportClick}>
          Talk to an Agent!
        </button>
      

      {showSupport && <LiveKitModal setShowSupport={setShowSupport}/>}
    </div>
  )
}

export default App
