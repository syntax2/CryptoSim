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
  const [miningStats, setMiningStats] = useState({
    totalBlocks: 0,
    miningRate: 0,
    isMining: false,
  });
  const [historicalData, setHistoricalData] = useState([]);

  useEffect(() => {
    // Poll for updates every second
    const interval = setInterval(fetchStats, 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch("/api/stats");
      const data = await response.json();
      setMiningStats(data);

      // Update historical data
      setHistoricalData((prev) =>
        [
          ...prev,
          {
            time: new Date().toLocaleTimeString(),
            rate: data.miningRate,
          },
        ].slice(-20)
      );
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  const toggleMining = async () => {
    const endpoint = miningStats.isMining ? "/api/stop" : "/api/start";
    try {
      await fetch(endpoint, { method: "POST" });
      fetchStats();
    } catch (error) {
      console.error("Error toggling mining:", error);
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

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900">
            CryptoSim Dashboard
          </h1>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
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
              {miningStats.miningRate.toFixed(2)} blocks/s
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

        {/* Chart */}
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
