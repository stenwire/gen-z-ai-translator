"use client";

import { useCoAgent, useCopilotAction } from "@copilotkit/react-core";
import { CopilotKitCSSProperties, CopilotPopup, Markdown } from "@copilotkit/react-ui";
import { useState } from "react";

export default function CopilotKitPage() {
  const [themeColor, setThemeColor] = useState("#090909ff");

  // 🪁 Frontend Actions: https://docs.copilotkit.ai/guides/frontend-actions
  useCopilotAction({
    name: "setThemeColor",
    parameters: [{
      name: "themeColor",
      description: "The theme color to set. Make sure to pick nice colors.",
      required: true,
    }],
    handler({ themeColor }) {
      setThemeColor(themeColor);
    },
  });

  return (
    <main style={{ "--copilot-kit-primary-color": themeColor } as CopilotKitCSSProperties}>
      <YourMainContent themeColor={themeColor} />
      <CopilotPopup
        // Button={}
        hitEscapeToClose={true}
        clickOutsideToClose={true}
        defaultOpen={true}
        labels={{
          title: "Gen-Z Assistant",
          initial: "👋 Hi, there! You're chatting with a Gen-Z agent. This agent comes with a few tools to get you started.\n\nFor example you can try:\n- **Frontend Tools**: \"Set the theme to orange\"\n- **Shared State**: \"Translate this to gen-z: I am so excited to start the year with a new car\"\n- **Generative UI**: \"Get the weather in SF\"\n\nAs you interact with the agent, you'll see the UI update in real-time to reflect the agent's **state**, **tool calls**, and **progress**."
        }}
      />
      <p>Chat</p>
    </main>
  );
}

// State of the agent, make sure this aligns with your agent's state.
type AgentState = {
  translations: string[];
}

function YourMainContent({ themeColor }: { themeColor: string }) {
  // 🪁 Shared State: https://docs.copilotkit.ai/coagents/shared-state
  const { state, setState } = useCoAgent<AgentState>({
    name: "my_agent",
    initialState: {
      translations: [
        "Original: Guys! I think am the hottest guy. Gen Z: Chat! Sigma skibidi alpha lit 🔥",
      ],
    },
  })

  useCopilotAction({
    name: "write_essay",
    available: "enabled",
    description: "Writes an essay and takes the draft as an argument.",
    parameters: [
      { name: "draft", type: "string", description: "The draft of the essay", required: true },
    ],
    renderAndWaitForResponse: ({ args, respond, status }) => {
      return (
        <div>
          <Markdown content={args.draft || 'Preparing your draft...'} />
          <div className={`flex gap-4 pt-4 ${status !== "executing" ? "hidden" : ""}`}>
            <button
              onClick={() => respond?.({ accepted: false })}
              disabled={status !== "executing"}
              className="border p-2 rounded-xl w-full"
            >
              Reject Draft
            </button>
            <button
              onClick={() => respond?.({ accepted: true })}
              disabled={status !== "executing"}
              className="bg-blue-500 text-white p-2 rounded-xl w-full"
            >
              Approve Draft
            </button>
          </div>
        </div>
      );
    }
  });

  useCopilotAction({
    name: "choose_translation_direction",
    available: "enabled",
    description: "Asks the user to choose a translation direction.",
    parameters: [
      { name: "text", type: "string", description: "The text to translate", required: true },
    ],
    renderAndWaitForResponse: ({ args, respond }) => {
      return (
        <div className="mt-4 mb-4 bg-black/20 backdrop-blur-lg p-6 rounded-xl">
          <h3 className="text-white text-lg font-semibold mb-4">
            What would you like to do with the text:
          </h3>
          <p className="text-white mb-6 italic">&ldquo;{args.text}&rdquo;</p>
          <div className="flex gap-4">
            <button
              onClick={() => {
                if (respond) respond({ direction: "to_genz" });
              }}
              className="border-2 border-blue-500 hover:bg-blue-500 hover:text-white text-blue-500 p-3 rounded-xl w-full transition-all duration-200 font-medium"
            >
              Translate to Gen-Z
            </button>
            <button
              onClick={() => {
                if (respond) respond({ direction: "to_english" });
              }}
              className="bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-xl w-full transition-all duration-200 font-medium"
            >
              Translate to English
            </button>
          </div>
        </div>
      );
    }
  });

  //🪁 Generative UI: https://docs.copilotkit.ai/coagents/generative-ui
  useCopilotAction({
    name: "get_weather",
    description: "Get the weather for a given location.",
    available: "disabled",
    parameters: [
      { name: "location", type: "string", required: true },
    ],
    render: ({ args }) => {
      return <WeatherCard location={args.location} themeColor={themeColor} />
    },
  });

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      alert('Copied to clipboard!');
    }).catch(err => {
      console.error('Failed to copy: ', err);
    });
  };

  return (
    <div
      style={{ backgroundColor: themeColor }}
      className="min-h-screen w-screen flex justify-center items-center flex-col transition-colors duration-300 p-4"
    >
      <div className="bg-white/30 backdrop-blur-lg p-8 rounded-2xl shadow-2xl max-w-6xl w-full">
        <h1 className="text-4xl font-bold text-white mb-2 text-center">Translations</h1>
        <p className="text-gray-200 text-center italic mb-6">Chat! Get ready to update your lingua.</p>
        <hr className="border-white/30 my-6" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {state.translations?.map((translation, index) => {
            const genZParts = translation.split(' Gen Z: ');
            const englishParts = translation.split(' English: ');
            let original = '';
            let translated = translation;

            if (genZParts.length === 2) {
              original = genZParts[0].startsWith('Original: ') ? genZParts[0].substring('Original: '.length) : genZParts[0];
              translated = genZParts[1];
            } else if (englishParts.length === 2) {
              original = englishParts[0].startsWith('Original: ') ? englishParts[0].substring('Original: '.length) : englishParts[0];
              translated = englishParts[1];
            }

            return (
              <div
                key={index}
                className="bg-white/20 p-4 rounded-xl text-white relative group hover:bg-white/30 transition-all duration-200 flex flex-col"
              >
                {original && (
                  <>
                    <h3 className="text-sm font-semibold mb-1">Original</h3>
                    <p className="text-sm mb-4">{original}</p>
                  </>
                )}
                <hr></hr>
                <br></br>
                <h3 className="text-sm font-semibold mb-1">{englishParts.length === 2 ? 'English Translation' : 'Gen Z Translation'}</h3>
                <p className="text-sm flex-grow">{translated}</p>
                <div className="absolute right-2 top-2 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => copyToClipboard(translated)}
                    className="rounded-lg bg-blue-500 hover:bg-blue-600 text-white br-2 h-6 w-10 flex items-center justify-center text-xs cursor-pointer"
                  >
                    {/* <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4">
                        <path d="M4 4.5A1.5 1.5 0 0 1 5.5 3h6A1.5 1.5 0 0 1 13 4.5v6A1.5 1.5 0 0 1 11.5 12h-6A1.5 1.5 0 0 1 4 10.5v-6Z" opacity="0.4" />
                        <path d="M3 5.5A1.5 1.5 0 0 1 4.5 4h6A1.5 1.5 0 0 1 12 5.5v6A1.5 1.5 0 0 1 10.5 13h-6A1.5 1.5 0 0 1 3 11.5v-6Z" />
                    </svg> */}
                    Copy
                  </button>
                  <button
                    onClick={() => setState({
                      ...state,
                      translations: state.translations?.filter((_, i) => i !== index),
                    })}
                    className="bg-red-500 hover:bg-red-600 text-white rounded-full h-6 w-6 flex items-center justify-center text-xs cursor-pointer"
                  >
                    ✕
                  </button>
                </div>
              </div>
            );
          })}
        </div>
        {state.translations?.length === 0 && (
          <p className="text-center text-white/80 italic my-8">
            No translations yet. Ask the assistant to add some!
          </p>
        )}
      </div>
    </div>
  );
}

// Simple sun icon for the weather card
function SunIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-14 h-14 text-yellow-200">
      <circle cx="12" cy="12" r="5" />
      <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" strokeWidth="2" stroke="currentColor" />
    </svg>
  );
}

// Weather card component where the location and themeColor are based on what the agent
// sets via tool calls.
function WeatherCard({ location, themeColor }: { location?: string, themeColor: string }) {
  return (
    <div
      style={{ backgroundColor: themeColor }}
      className="rounded-xl shadow-xl mt-6 mb-4 max-w-md w-full"
    >
      <div className="bg-white/20 p-4 w-full">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-white capitalize">{location}</h3>
            <p className="text-white">Current Weather</p>
          </div>
          <SunIcon />
        </div>
        <div className="mt-4 flex items-end justify-between">
          <div className="text-3xl font-bold text-white">70°</div>
          <div className="text-sm text-white">Clear skies</div>
        </div>
        <div className="mt-4 pt-4 border-t border-white">
          <div className="grid grid-cols-3 gap-2 text-center">
            <div>
              <p className="text-white text-xs">Humidity</p>
              <p className="text-white font-medium">45%</p>
            </div>
            <div>
              <p className="text-white text-xs">Wind</p>
              <p className="text-white font-medium">5 mph</p>
            </div>
            <div>
              <p className="text-white text-xs">Feels Like</p>
              <p className="text-white font-medium">72°</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
