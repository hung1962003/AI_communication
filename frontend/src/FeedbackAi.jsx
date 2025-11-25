import dayjs from "dayjs";
import { useEffect, useState } from "react";

const Feedback = () => {
  const [messages, setMessages] = useState([]);
  const [feedbackSections, setFeedbackSections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 📍 Load messages from localStorage and fetch feedback
  useEffect(() => {
    const loadMessagesAndFetchFeedback = async () => {
      const data = localStorage.getItem("messages");
      if (data) {
        try {
          const parsedMessages = JSON.parse(data);
          setMessages(parsedMessages);

          // If we have messages, fetch feedback
          if (parsedMessages.length > 0) {
            // Check if there are any user messages
            const userMessages = parsedMessages.filter(
              (msg) => msg.type === "user" && (msg.text || msg.transcription)
            );
            
            // If no user messages, show special feedback
            if (userMessages.length === 0) {
              setLoading(false);
              setFeedbackSections([
                {
                  title: "No User Input",
                  description: "You haven't spoken yet in this conversation. Please start speaking to receive feedback on your English pronunciation and accent.",
                  items: [],
                },
                {
                  title: "Chưa có phản hồi từ người dùng",
                  description: "Bạn chưa nói trong cuộc trò chuyện này. Vui lòng bắt đầu nói để nhận phản hồi về phát âm và giọng tiếng Anh của bạn.",
                  items: [],
                },
              ]);
              return;
            }

            setLoading(true);
            setError(null);
            setFeedbackSections([]);

            try {
              // Combine messages into text format
              const conversationText = parsedMessages
                .map((msg) => {
                  const speaker = msg.type === "agent" ? "Agent" : "You";
                  const text = msg.text || msg.transcription || "";
                  return `${speaker}: ${text}`;
                })
                .join("\n");
              
              console.log("conversationText (useEffect):", conversationText);
              console.log("parsedMessages:", parsedMessages);

              // Call the API
              const response = await fetch("/api/aiFeedback/", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  text: conversationText,
                  bilingual: true,
                }),
              });

              if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
              }

              const data = await response.json();
              setFeedbackSections(parseFeedback(data.feedback || ""));
            } catch (err) {
              console.error("Error fetching feedback:", err);
              setError(err.message || "Failed to fetch feedback");
            } finally {
              setLoading(false);
            }
          }
        } catch (err) {
          console.error("Error parsing messages:", err);
          setError("Failed to load messages");
        }
      }
    };

    loadMessagesAndFetchFeedback();
  }, []);

  const fetchFeedback = async () => {
    // Check if there are any user messages
    const userMessages = messages.filter(
      (msg) => msg.type === "user" && (msg.text || msg.transcription)
    );
    
    // If no user messages, show special feedback
    if (userMessages.length === 0) {
      setLoading(false);
      setFeedbackSections([
        {
          title: "No User Input",
          description: "You haven't spoken yet in this conversation. Please start speaking to receive feedback on your English pronunciation and accent.",
          items: [],
        },
        {
          title: "Chưa có phản hồi từ người dùng",
          description: "Bạn chưa nói trong cuộc trò chuyện này. Vui lòng bắt đầu nói để nhận phản hồi về phát âm và giọng tiếng Anh của bạn.",
          items: [],
        },
      ]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log("fetchFeedback called, messages:", messages);
      // Combine messages into text format
      const conversationText = messages
        .map((msg) => {
          const speaker = msg.type === "agent" ? "Agent" : "You";
          const text = msg.text || msg.transcription || "";
          return `${speaker}: ${text}`;
        })
        .join("\n");
      console.log("conversationText (fetchFeedback):", conversationText);
      // Call the API
      const response = await fetch("/api/aiFeedback/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: conversationText,
          bilingual: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setFeedbackSections(parseFeedback(data.feedback || ""));
    } catch (err) {
      console.error("Error fetching feedback:", err);
      setError(err.message || "Failed to fetch feedback");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="section-feedback">
      <div className="flex flex-row justify-center">
        <h1 className="text-4xl font-semibold">
          Feedback on the conversation
        </h1>
      </div>

      <div className="flex flex-row justify-center">
        <div className="flex flex-row gap-5">
          {/* Date */}
          <div className="flex flex-row gap-2">
            <p>
              {dayjs().format("MMM D, YYYY h:mm A")}
            </p>
          </div>
        </div>
      </div>

      <hr />

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center items-center p-8">
          <p>Loading feedback...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="flex flex-col gap-3 p-4 bg-red-100 rounded">
          <h3 className="font-bold text-red-800">Error</h3>
          <p className="text-red-600">{error}</p>
          <button
            onClick={fetchFeedback}
            className="btn-primary px-4 py-2 rounded"
          >
            Retry
          </button>
        </div>
      )}

      {/* Feedback Content */}
      {!loading && !error && feedbackSections.length > 0 && (
        <div className="flex flex-col gap-6">
          {feedbackSections.map((section, idx) => (
            <article key={idx} className="p-4 rounded border border-gray-200 shadow-sm">
              {section.title && (
                <h2 className="text-xl font-semibold mb-2">{section.title}</h2>
              )}
              {section.description && (
                <p className="text-gray-700 leading-relaxed">{section.description}</p>
              )}
              {section.items.length > 0 && (
                <ul className="list-disc list-inside mt-3 space-y-2 text-gray-700">
                  {section.items.map((item, itemIdx) => (
                    <li key={itemIdx}>{item}</li>
                  ))}
                </ul>
              )}
            </article>
          ))}
        </div>
      )}

      {/* No messages state */}
      {!loading && !error && messages.length === 0 && (
        <div className="flex flex-col gap-3 p-4">
          <p>No conversation messages found. Please start a conversation first.</p>
        </div>
      )}

      <div className="buttons">
        <button className="btn-secondary flex-1">
          <a href="/" className="flex w-full justify-center">
            <p className="text-sm font-semibold text-primary-200 text-center">
              Back to dashboard
            </p>
          </a>
        </button>
      </div>
    </section>
  );
};

const parseFeedback = (text) => {
  if (!text) return [];

  const sections = [];
  let currentSection = null;

  const pushCurrentSection = () => {
    if (currentSection) {
      sections.push({
        title: currentSection.title,
        description: currentSection.description.trim(),
        items: currentSection.items,
      });
    }
  };

  text.split("\n").forEach((rawLine) => {
    const line = rawLine.trim();
    if (!line) return;

    const sectionMatch = line.match(/^\*\*(.+?)\*\*:?(.+)?$/);

    if (sectionMatch) {
      pushCurrentSection();
      currentSection = {
        title: sectionMatch[1],
        description: sectionMatch[2]?.trim() ?? "",
        items: [],
      };
      return;
    }

    if (!currentSection) {
      currentSection = { title: "", description: "", items: [] };
    }

    const listMatch = line.match(/^\d+\.\s*(.+)$/);
    if (listMatch) {
      currentSection.items.push(listMatch[1]);
      return;
    }

    if (currentSection.items.length > 0) {
      currentSection.items[currentSection.items.length - 1] += ` ${line}`;
    } else if (currentSection.description) {
      currentSection.description += ` ${line}`;
    } else {
      currentSection.description = line;
    }
  });

  pushCurrentSection();

  return sections.filter(
    (section) =>
      section.title || section.description || section.items.length > 0
  );
};

export default Feedback;
