// import React, { useState, useEffect } from "react";
// import { Line } from "react-chartjs-2";
// import {
//   Chart as ChartJS,
//   CategoryScale,
//   LinearScale,
//   PointElement,
//   LineElement,
//   Title,
//   Tooltip,
//   Legend,
//   Filler,
// } from "chart.js";

// // Register ChartJS components
// ChartJS.register(
//   CategoryScale,
//   LinearScale,
//   PointElement,
//   LineElement,
//   Title,
//   Tooltip,
//   Legend,
//   Filler
// );

// const App = () => {
//   const [miningStats, setMiningStats] = useState({
//     totalBlocks: 0,
//     miningRate: 0,
//     isMining: false,
//   });
//   const [historicalData, setHistoricalData] = useState([]);

//   useEffect(() => {
//     // Poll for updates every second
//     const interval = setInterval(fetchStats, 1000);
//     return () => clearInterval(interval);
//   }, []);

//   const fetchStats = async () => {
//     try {
//       const response = await fetch("/api/stats");
//       const data = await response.json();
//       setMiningStats(data);

//       // Update historical data
//       setHistoricalData((prev) =>
//         [
//           ...prev,
//           {
//             time: new Date().toLocaleTimeString(),
//             rate: data.miningRate,
//           },
//         ].slice(-20)
//       );
//     } catch (error) {
//       console.error("Error fetching stats:", error);
//     }
//   };

//   const toggleMining = async () => {
//     const endpoint = miningStats.isMining ? "/api/stop" : "/api/start";
//     try {
//       await fetch(endpoint, { method: "POST" });
//       fetchStats();
//     } catch (error) {
//       console.error("Error toggling mining:", error);
//     }
//   };

//   const chartData = {
//     labels: historicalData.map((d) => d.time),
//     datasets: [
//       {
//         label: "Mining Rate (blocks/s)",
//         data: historicalData.map((d) => d.rate),
//         fill: true,
//         borderColor: "rgb(75, 192, 192)",
//         backgroundColor: "rgba(75, 192, 192, 0.2)",
//         tension: 0.4,
//       },
//     ],
//   };

//   return (
//     <div className="min-h-screen bg-gray-100">
//       <nav className="bg-white shadow-lg">
//         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
//           <h1 className="text-3xl font-bold text-gray-900">
//             CryptoSim Dashboard
//           </h1>
//         </div>
//       </nav>

//       <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
//         {/* Stats Grid */}
//         <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
//           <div className="bg-white rounded-lg shadow p-6">
//             <h2 className="text-xl font-semibold text-gray-700 mb-2">
//               Total Blocks Mined
//             </h2>
//             <p className="text-4xl font-bold text-indigo-600">
//               {miningStats.totalBlocks}
//             </p>
//           </div>

//           <div className="bg-white rounded-lg shadow p-6">
//             <h2 className="text-xl font-semibold text-gray-700 mb-2">
//               Current Mining Rate
//             </h2>
//             <p className="text-4xl font-bold text-green-600">
//               {miningStats.miningRate.toFixed(2)} blocks/s
//             </p>
//           </div>

//           <div className="bg-white rounded-lg shadow p-6">
//             <h2 className="text-xl font-semibold text-gray-700 mb-2">
//               Mining Status
//             </h2>
//             <button
//               onClick={toggleMining}
//               className={`w-full py-2 px-4 rounded-md text-white font-semibold ${
//                 miningStats.isMining
//                   ? "bg-red-500 hover:bg-red-600"
//                   : "bg-green-500 hover:bg-green-600"
//               }`}
//             >
//               {miningStats.isMining ? "Stop Mining" : "Start Mining"}
//             </button>
//           </div>
//         </div>

//         {/* Chart */}
//         <div className="bg-white rounded-lg shadow p-6">
//           <h2 className="text-xl font-semibold text-gray-700 mb-4">
//             Mining Performance
//           </h2>
//           <div className="h-96">
//             <Line
//               data={chartData}
//               options={{
//                 responsive: true,
//                 maintainAspectRatio: false,
//                 scales: {
//                   y: {
//                     beginAtZero: true,
//                   },
//                 },
//                 plugins: {
//                   legend: {
//                     display: true,
//                     position: "top",
//                   },
//                 },
//               }}
//             />
//           </div>
//         </div>
//       </main>

//       <footer className="bg-white shadow-lg mt-8">
//         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
//           <p className="text-center text-gray-600">
//             CryptoSim - Educational Cryptocurrency Mining Simulator
//           </p>
//         </div>
//       </footer>
//     </div>
//   );
// };

// export default App;

import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const App = () => {
  // Initialize state with default values to prevent undefined errors
  const [miningStats, setMiningStats] = useState({
    totalBlocks: 0,
    miningRate: 0,
    isMining: false,
  });
  const [historicalData, setHistoricalData] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initial fetch when component mounts
    fetchStats();

    // Set up polling interval
    const interval = setInterval(fetchStats, 1000);

    // Cleanup interval on component unmount
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      setError(null);
      const response = await fetch("/api/stats");
      if (!response.ok) {
        throw new Error("Failed to fetch stats");
      }
      const data = await response.json();

      // Update mining stats with safe fallbacks
      setMiningStats({
        totalBlocks: data.totalBlocks || 0,
        miningRate: data.miningRate || 0,
        isMining: !!data.isMining,
      });

      // Update historical data
      setHistoricalData((prev) =>
        [
          ...prev,
          {
            time: new Date().toLocaleTimeString(),
            rate: data.miningRate || 0,
          },
        ].slice(-20)
      ); // Keep last 20 data points

      setLoading(false);
    } catch (error) {
      console.error("Error fetching stats:", error);
      setError(error.message);
      setLoading(false);
    }
  };

  const toggleMining = async () => {
    try {
      const endpoint = miningStats.isMining ? "/api/stop" : "/api/start";
      const response = await fetch(endpoint, { method: "POST" });
      if (!response.ok) {
        throw new Error("Failed to toggle mining");
      }
      await fetchStats();
    } catch (error) {
      console.error("Error toggling mining:", error);
      setError(error.message);
    }
  };

  const chartData = {
    labels: historicalData.map((d) => d.time),
    datasets: [
      {
        label: "Mining Rate (blocks/s)",
        data: historicalData.map((d) => d.rate),
        fill: true,
        borderColor: "rgb(75, 192, 192)",
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        tension: 0.4,
      },
    ],
  };

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-xl font-semibold text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900">
            CryptoSim Dashboard
          </h1>
        </div>
      </nav>

      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div
            className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative"
            role="alert"
          >
            <span className="block sm:inline">{error}</span>
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-700 mb-2">
              Total Blocks Mined
            </h2>
            <p className="text-4xl font-bold text-indigo-600">
              {miningStats.totalBlocks}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-700 mb-2">
              Current Mining Rate
            </h2>
            <p className="text-4xl font-bold text-green-600">
              {/* Add null check before using toFixed */}
              {typeof miningStats.miningRate === "number"
                ? `${miningStats.miningRate.toFixed(2)} blocks/s`
                : "0.00 blocks/s"}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-700 mb-2">
              Mining Status
            </h2>
            <button
              onClick={toggleMining}
              className={`w-full py-2 px-4 rounded-md text-white font-semibold ${
                miningStats.isMining
                  ? "bg-red-500 hover:bg-red-600"
                  : "bg-green-500 hover:bg-green-600"
              }`}
            >
              {miningStats.isMining ? "Stop Mining" : "Start Mining"}
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            Mining Performance
          </h2>
          <div className="h-96">
            <Line
              data={chartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: true,
                  },
                },
                plugins: {
                  legend: {
                    display: true,
                    position: "top",
                  },
                },
              }}
            />
          </div>
        </div>
      </main>

      <footer className="bg-white shadow-lg mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-gray-600">
            CryptoSim - Educational Cryptocurrency Mining Simulator
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;
