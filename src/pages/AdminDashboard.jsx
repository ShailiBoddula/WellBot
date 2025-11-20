import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [kbEntries, setKbEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [userStats, setUserStats] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/');
      return;
    }
    checkUserRole();
    fetchUserStats();
    fetchStats();
    fetchKbEntries();
  }, [navigate]);

  const checkUserRole = async () => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:8000/user/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setIsAdmin(data.is_admin || false);
      }
    } catch (error) {
      console.error('Failed to check user role:', error);
    }
  };

  const fetchUserStats = async () => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:8000/user/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUserStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch user stats:', error);
    }
  };

  const fetchStats = async () => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:8000/admin/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchKbEntries = async () => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:8000/admin/kb', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setKbEntries(data.entries);
      }
    } catch (error) {
      console.error('Failed to fetch KB entries:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddKbEntry = async (entry) => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:8000/admin/kb', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(entry)
      });
      if (response.ok) {
        fetchKbEntries();
        setShowAddModal(false);
      }
    } catch (error) {
      console.error('Failed to add KB entry:', error);
    }
  };

  const handleUpdateKbEntry = async (id, entry) => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`http://localhost:8000/admin/kb/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(entry)
      });
      if (response.ok) {
        fetchKbEntries();
        setEditingEntry(null);
      }
    } catch (error) {
      console.error('Failed to update KB entry:', error);
    }
  };

  const handleDeleteKbEntry = async (id) => {
    if (!confirm('Are you sure you want to delete this entry?')) return;
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`http://localhost:8000/admin/kb/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        fetchKbEntries();
      }
    } catch (error) {
      console.error('Failed to delete KB entry:', error);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-900 text-white p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 text-white min-h-screen p-8">
      <div className="w-full max-w-7xl mx-auto p-4">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <button
            onClick={() => {
              localStorage.removeItem('token');
              navigate('/');
            }}
            className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg"
          >
            Logout
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex gap-4 mb-8">
          <button
            onClick={() => setActiveTab("dashboard")}
            className={`px-4 py-2 rounded-md font-medium transition
    ${activeTab === "dashboard"
      ? "bg-blue-500 text-white"
      : "bg-gray-700 text-gray-300 hover:bg-gray-600"}`}
          >
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-4 py-2 rounded-md font-medium transition
    ${activeTab === "analytics"
      ? "bg-blue-500 text-white"
      : "bg-gray-700 text-gray-300 hover:bg-gray-600"}`}
          >
            Analytics
          </button>
          <button
            onClick={() => setActiveTab('knowledge-base')}
            className={`px-4 py-2 rounded-md font-medium transition
    ${activeTab === "knowledge-base"
      ? "bg-blue-500 text-white"
      : "bg-gray-700 text-gray-300 hover:bg-gray-600"}`}
          >
            Knowledge Base
          </button>
          <button
            onClick={() => setActiveTab('feedback')}
            className={`px-4 py-2 rounded-md font-medium transition
    ${activeTab === "feedback"
      ? "bg-blue-500 text-white"
      : "bg-gray-700 text-gray-300 hover:bg-gray-600"}`}
          >
            Feedback
          </button>
        </div>

        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {isAdmin ? (
                <>
                  <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                    <h3 className="text-lg font-semibold mb-2">Total Users</h3>
                    <p className="text-3xl font-bold text-blue-400">{stats?.total_users || 0}</p>
                  </div>
                  <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                    <h3 className="text-lg font-semibold mb-2">Total Conversations</h3>
                    <p className="text-3xl font-bold text-green-400">{stats?.total_conversations || 0}</p>
                  </div>
                  <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                    <h3 className="text-lg font-semibold mb-2">Total Messages</h3>
                    <p className="text-3xl font-bold text-purple-400">{stats?.total_messages || 0}</p>
                  </div>
                  <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                    <h3 className="text-lg font-semibold mb-2">Positive Feedback</h3>
                    <p className="text-3xl font-bold text-yellow-400">{stats?.positive_feedback || '0%'}</p>
                  </div>
                </>
              ) : (
                <>
                  <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                    <h3 className="text-lg font-semibold mb-2">My Conversations</h3>
                    <p className="text-3xl font-bold text-blue-400">{userStats?.conversations_count || 0}</p>
                  </div>
                  <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                    <h3 className="text-lg font-semibold mb-2">My Messages</h3>
                    <p className="text-3xl font-bold text-green-400">{userStats?.messages_count || 0}</p>
                  </div>
                  <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                    <h3 className="text-lg font-semibold mb-2">My Feedback</h3>
                    <p className="text-3xl font-bold text-purple-400">
                      {userStats?.feedback_stats ? Object.values(userStats.feedback_stats).reduce((a, b) => a + b, 0) : 0}
                    </p>
                  </div>
                  <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                    <h3 className="text-lg font-semibold mb-2">Account Status</h3>
                    <p className="text-lg font-bold text-yellow-400">Active</p>
                  </div>
                </>
              )}
            </div>

            {/* User-Specific Analytics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {isAdmin ? (
                <>
                  <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                    <h3 className="text-xl font-semibold mb-4">Feedback Distribution</h3>
                    <div className="space-y-3">
                      {stats?.feedback_stats && Object.entries(stats.feedback_stats).map(([type, count]) => {
                        const total = Object.values(stats.feedback_stats).reduce((a, b) => a + b, 0);
                        const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                        return (
                          <div key={type} className="space-y-1">
                            <div className="flex justify-between text-sm">
                              <span className="capitalize">{type}</span>
                              <span>{count} ({percentage}%)</span>
                            </div>
                            <div className="w-full bg-gray-700 rounded-full h-2">
                              <div
                                className="bg-blue-500 h-2 rounded-full"
                                style={{ width: `${percentage}%` }}
                              ></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                    <h3 className="text-xl font-semibold mb-4">Top Queries</h3>
                    <div className="space-y-3">
                      {stats?.common_queries?.slice(0, 5).map(([query, count], index) => (
                        <div key={index} className="flex items-center justify-between">
                          <span className="truncate flex-1 mr-4 text-sm">{query}</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-700 rounded-full h-2">
                              <div
                                className="bg-green-500 h-2 rounded-full"
                                style={{ width: `${Math.min((count / (stats.common_queries[0]?.[1] || 1)) * 100, 100)}%` }}
                              ></div>
                            </div>
                            <span className="font-bold text-sm w-8 text-right">{count}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                    <h3 className="text-xl font-semibold mb-4">My Chat History</h3>
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-blue-400 mb-2">{userStats?.conversations_count || 0}</div>
                        <p className="text-gray-400">Total Conversations</p>
                      </div>
                      <div className="text-center">
                        <div className="text-3xl font-bold text-green-400 mb-2">{userStats?.messages_count || 0}</div>
                        <p className="text-gray-400">Total Messages</p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                    <h3 className="text-xl font-semibold mb-4">My Feedback</h3>
                    <div className="space-y-3">
                      {userStats?.feedback_stats && Object.entries(userStats.feedback_stats).map(([type, count]) => (
                        <div key={type} className="flex justify-between">
                          <span className="capitalize">{type} Feedback</span>
                          <span className="font-bold">{count}</span>
                        </div>
                      ))}
                      {userStats?.common_queries?.slice(0, 3).map(([query, count], index) => (
                        <div key={index} className="border-t border-gray-700 pt-2 mt-2">
                          <p className="text-sm text-gray-400">Recent query:</p>
                          <p className="text-sm truncate">{query}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && stats && (
          <div className="space-y-8">
            {/* Query Trends Over Time */}
            <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
              <h3 className="text-xl font-semibold mb-4">Query Trends Over Time</h3>
              <div className="h-64 relative">
                <svg viewBox="0 0 400 200" className="w-full h-full">
                  {/* Grid lines */}
                  <line x1="0" y1="180" x2="400" y2="180" stroke="#374151" strokeWidth="1"/>
                  <line x1="0" y1="135" x2="400" y2="135" stroke="#374151" strokeWidth="1"/>
                  <line x1="0" y1="90" x2="400" y2="90" stroke="#374151" strokeWidth="1"/>
                  <line x1="0" y1="45" x2="400" y2="45" stroke="#374151" strokeWidth="1"/>
                  <line x1="0" y1="0" x2="400" y2="0" stroke="#374151" strokeWidth="1"/>

                  {/* Y-axis labels */}
                  <text x="-10" y="185" className="text-xs fill-gray-400">0</text>
                  <text x="-10" y="140" className="text-xs fill-gray-400">25</text>
                  <text x="-10" y="95" className="text-xs fill-gray-400">50</text>
                  <text x="-10" y="50" className="text-xs fill-gray-400">75</text>
                  <text x="-10" y="5" className="text-xs fill-gray-400">100</text>

                  {/* Data points and line */}
                  {(() => {
                    const dayOrder = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                    const data = dayOrder.map(day => ({
                      day,
                      queries: stats?.query_trends?.[day] || 0
                    }));

                    const points = data.map((item, index) => {
                      const x = 50 + (index * 50);
                      const y = 180 - (item.queries / 100 * 180);
                      return `${x},${y}`;
                    }).join(' ');

                    return (
                      <>
                        {/* Line */}
                        <polyline
                          points={points}
                          fill="none"
                          stroke="#3B82F6"
                          strokeWidth="3"
                          strokeLinejoin="round"
                          strokeLinecap="round"
                        />

                        {/* Data points */}
                        {data.map((item, index) => {
                          const x = 50 + (index * 50);
                          const y = 180 - (item.queries / 100 * 180);
                          return (
                            <circle
                              key={index}
                              cx={x}
                              cy={y}
                              r="4"
                              fill="#3B82F6"
                              stroke="#1E40AF"
                              strokeWidth="2"
                            />
                          );
                        })}

                        {/* X-axis labels */}
                        {data.map((item, index) => (
                          <text
                            key={index}
                            x={50 + (index * 50)}
                            y="200"
                            className="text-xs fill-gray-400 text-center"
                            textAnchor="middle"
                          >
                            {item.day}
                          </text>
                        ))}
                      </>
                    );
                  })()}
                </svg>
              </div>
              <p className="text-sm text-gray-400 mt-2">Weekly query volume trends</p>
            </div>

            {/* Top Query Categories */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                <h3 className="text-xl font-semibold mb-4">Top Query Categories</h3>
                <div className="flex items-center justify-center">
                  <div className="relative w-64 h-64">
                    <svg viewBox="0 0 100 100" className="w-full h-full">
                      {(() => {
                        const topics = Object.entries(stats.health_topics || {});
                        let cumulativePercentage = 0;
                        const colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];
  
                        return topics.map(([topic, data], index) => {
                          const startAngle = (cumulativePercentage / 100) * 360;
                          const endAngle = ((cumulativePercentage + data.percentage) / 100) * 360;
                          cumulativePercentage += data.percentage;
  
                          const x1 = 50 + 40 * Math.cos((startAngle * Math.PI) / 180);
                          const y1 = 50 + 40 * Math.sin((startAngle * Math.PI) / 180);
                          const x2 = 50 + 40 * Math.cos((endAngle * Math.PI) / 180);
                          const y2 = 50 + 40 * Math.sin((endAngle * Math.PI) / 180);
  
                          const largeArcFlag = endAngle - startAngle > 180 ? 1 : 0;
  
                          return (
                            <path
                              key={index}
                              d={`M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArcFlag} 1 ${x2} ${y2} Z`}
                              fill={colors[index % colors.length]}
                            />
                          );
                        });
                      })()}
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-2xl font-bold">{Object.keys(stats.health_topics || {}).length}</div>
                        <div className="text-sm text-gray-400">Categories</div>
                      </div>
                    </div>
                  </div>
                  <div className="ml-8 space-y-3">
                    {Object.entries(stats.health_topics || {}).map(([topic, data], index) => {
                      const colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];
                      return (
                        <div key={index} className="flex items-center space-x-3">
                          <div
                            className="w-4 h-4 rounded"
                            style={{ backgroundColor: colors[index % colors.length] }}
                          ></div>
                          <div className="flex-1">
                            <div className="text-sm font-medium">{topic}</div>
                            <div className="text-xs text-gray-400">{data.count} queries ({data.percentage}%)</div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                <h3 className="text-xl font-semibold mb-4">User Engagement Metrics</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span>Total Users</span>
                    <span className="font-bold">{stats.total_users}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Total Conversations</span>
                    <span className="font-bold">{stats.total_conversations}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Average Messages/Conversation</span>
                    <span className="font-bold">
                      {stats.total_conversations > 0 ? (stats.total_messages / stats.total_conversations).toFixed(1) : 0}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Feedback Response Rate</span>
                    <span className="font-bold">
                      {Object.values(stats.feedback_stats || {}).reduce((a, b) => a + b, 0) > 0 ?
                        Math.round((Object.values(stats.feedback_stats || {}).reduce((a, b) => a + b, 0) / stats.total_messages) * 100) : 0}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'feedback' && stats && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                <h3 className="text-xl font-semibold mb-4">Feedback Overview</h3>
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-4xl font-bold text-green-400 mb-2">{stats.positive_feedback}</div>
                    <p className="text-gray-400">Positive Feedback Rate</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-400">{stats.feedback_stats.positive || 0}</div>
                      <p className="text-sm text-gray-400">👍 Positive</p>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-400">{stats.feedback_stats.negative || 0}</div>
                      <p className="text-sm text-gray-400">👎 Negative</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
                <h3 className="text-xl font-semibold mb-4">Recent Feedback</h3>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {stats.recent_feedback && stats.recent_feedback.length > 0 ? (
                    stats.recent_feedback.map((feedback, index) => (
                      <div key={index} className={`border-l-4 ${feedback.type === 'positive' ? 'border-green-500' : 'border-red-500'} pl-4 py-2`}>
                        <p className="text-sm">{feedback.comment}</p>
                        <p className="text-xs text-gray-400">
                          {new Date(feedback.timestamp).toLocaleDateString()} at {new Date(feedback.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-gray-400">No feedback received yet. Start chatting to collect feedback!</p>
                  )}
                </div>
              </div>
            </div>

            <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
              <h3 className="text-xl font-semibold mb-4">Feedback Trends</h3>
              <div className="h-48 flex items-end justify-between space-x-1">
                {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, index) => {
                  const dayData = stats?.feedback_trends?.[day] || { positive: 0, negative: 0 };
                  const total = dayData.positive + dayData.negative;
                  const maxHeight = 100; // Max height in px
                  const scale = total > 0 ? maxHeight / Math.max(total, 10) : 0; // Scale to fit
                  return (
                    <div key={index} className="flex flex-col items-center flex-1">
                      <div className="w-full flex space-x-0.5">
                        <div
                          className="bg-green-500 rounded-t flex-1"
                          style={{ height: `${dayData.positive * scale}px` }}
                        ></div>
                        <div
                          className="bg-red-500 rounded-t flex-1"
                          style={{ height: `${dayData.negative * scale}px` }}
                        ></div>
                      </div>
                      <span className="text-xs mt-2 text-gray-400">
                        {day}
                      </span>
                    </div>
                  );
                })}
              </div>
              <div className="flex justify-center gap-6 mt-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded"></div>
                  <span className="text-sm">Positive</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded"></div>
                  <span className="text-sm">Negative</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'knowledge-base' && (
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Knowledge Base Management</h2>
              <button
                onClick={() => setShowAddModal(true)}
                className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg"
              >
                Add Entry
              </button>
            </div>

            <div className="space-y-4">
              {kbEntries.map((entry) => (
                <div key={entry[0]} className="bg-gray-700 p-4 rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-semibold">{entry[2]}</h3>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setEditingEntry(entry)}
                        className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteKbEntry(entry[0])}
                        className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                  <p className="text-gray-300 mb-2">{entry[3]}</p>
                  <p className="text-gray-400 text-sm">Category: {entry[1]}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Add/Edit Modal */}
        {(showAddModal || editingEntry) && (
          <KbEntryModal
            entry={editingEntry}
            onSave={editingEntry ? (entry) => handleUpdateKbEntry(editingEntry[0], entry) : handleAddKbEntry}
            onClose={() => {
              setShowAddModal(false);
              setEditingEntry(null);
            }}
          />
        )}
      </div>
    </div>
  );
}

function KbEntryModal({ entry, onSave, onClose }) {
  const [formData, setFormData] = useState({
    category: entry ? entry[1] : '',
    title: entry ? entry[2] : '',
    content_english: entry ? entry[3] : '',
    content_hindi: entry ? entry[4] : '',
    keywords: entry ? entry[5] : ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 p-6 rounded-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h3 className="text-xl font-bold mb-4">{entry ? 'Edit' : 'Add'} Knowledge Base Entry</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Category</label>
            <input
              type="text"
              value={formData.category}
              onChange={(e) => setFormData({...formData, category: e.target.value})}
              className="w-full p-2 bg-gray-700 border border-gray-600 rounded"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              className="w-full p-2 bg-gray-700 border border-gray-600 rounded"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Content (English)</label>
            <textarea
              value={formData.content_english}
              onChange={(e) => setFormData({...formData, content_english: e.target.value})}
              className="w-full p-2 bg-gray-700 border border-gray-600 rounded h-24"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Content (Hindi)</label>
            <textarea
              value={formData.content_hindi}
              onChange={(e) => setFormData({...formData, content_hindi: e.target.value})}
              className="w-full p-2 bg-gray-700 border border-gray-600 rounded h-24"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Keywords (comma-separated)</label>
            <input
              type="text"
              value={formData.keywords}
              onChange={(e) => setFormData({...formData, keywords: e.target.value})}
              className="w-full p-2 bg-gray-700 border border-gray-600 rounded"
              required
            />
          </div>
          <div className="flex gap-2 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded"
            >
              {entry ? 'Update' : 'Add'} Entry
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}