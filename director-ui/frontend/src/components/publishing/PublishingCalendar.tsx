import React, { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, Plus, Clock, Video, Users } from 'lucide-react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, isToday } from 'date-fns';
import { apiUrl } from '../../config/api';

interface ScheduledPublish {
  id: string;
  title: string;
  video_path: string;
  platforms: string[];
  scheduled_time: string;
  account_id: string;
  status: 'pending' | 'scheduled' | 'completed' | 'failed';
}

interface PublishingCalendarProps {
  onSchedule: () => void;
}

const PublishingCalendar: React.FC<PublishingCalendarProps> = ({ onSchedule }) => {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [scheduledPublishes, setScheduledPublishes] = useState<ScheduledPublish[]>([]);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [accounts, setAccounts] = useState<any[]>([]);

  useEffect(() => {
    fetchScheduledPublishes();
    fetchAccounts();
  }, [currentMonth]);

  const fetchScheduledPublishes = async () => {
    try {
      const start = startOfMonth(currentMonth);
      const end = endOfMonth(currentMonth);
      const response = await fetch(
        apiUrl(`/api/publishing/jobs?status=pending,scheduled&limit=100`)
      );
      const data = await response.json();
      setScheduledPublishes(data.jobs || []);
    } catch (error) {
      console.error('Error fetching scheduled publishes:', error);
    }
  };

  const fetchAccounts = async () => {
    try {
      const response = await fetch(apiUrl('/api/publishing/accounts'));
      const data = await response.json();
      setAccounts(data.accounts || []);
    } catch (error) {
      console.error('Error fetching accounts:', error);
    }
  };

  const getDaysInMonth = () => {
    const start = startOfMonth(currentMonth);
    const end = endOfMonth(currentMonth);
    return eachDayOfInterval({ start, end });
  };

  const getPublishesForDate = (date: Date) => {
    return scheduledPublishes.filter(pub => {
      const pubDate = new Date(pub.scheduled_time);
      return isSameDay(pubDate, date);
    });
  };

  const days = getDaysInMonth();
  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-blue-500 border-opacity-30 max-w-[1920px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <CalendarIcon className="w-6 h-6 text-blue-400" />
          <h2 className="text-2xl font-bold">Publishing Calendar</h2>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
            className="px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg"
          >
            ←
          </button>
          <div className="px-4 py-2 bg-gray-800 rounded-lg font-semibold">
            {format(currentMonth, 'MMMM yyyy')}
          </div>
          <button
            onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
            className="px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg"
          >
            →
          </button>
          <button
            onClick={() => setShowScheduleModal(true)}
            className="ml-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Schedule Publish</span>
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-2">
        {/* Week day headers */}
        {weekDays.map(day => (
          <div key={day} className="text-center font-semibold text-gray-400 py-2">
            {day}
          </div>
        ))}

        {/* Days */}
        {days.map(day => {
          const publishes = getPublishesForDate(day);
          const isCurrentMonth = isSameMonth(day, currentMonth);
          const isSelected = selectedDate && isSameDay(day, selectedDate);
          const isDayToday = isToday(day);

          return (
            <div
              key={day.toISOString()}
              onClick={() => setSelectedDate(day)}
              className={`
                min-h-24 p-2 rounded-lg cursor-pointer border-2 transition-all
                ${!isCurrentMonth ? 'opacity-40 bg-gray-900' : 'bg-gray-800'}
                ${isSelected ? 'border-blue-500' : 'border-transparent'}
                ${isDayToday ? 'ring-2 ring-green-500' : ''}
                hover:border-blue-400
              `}
            >
              <div className={`text-sm font-semibold mb-1 ${isDayToday ? 'text-green-400' : ''}`}>
                {format(day, 'd')}
              </div>
              <div className="space-y-1">
                {publishes.slice(0, 3).map(pub => (
                  <div
                    key={pub.id}
                    className="text-xs px-2 py-1 bg-blue-600 bg-opacity-50 rounded truncate"
                    title={pub.title}
                  >
                    <div className="flex items-center space-x-1">
                      <Video className="w-3 h-3" />
                      <span className="truncate">{pub.title}</span>
                    </div>
                    <div className="text-xs text-gray-300">
                      {format(new Date(pub.scheduled_time), 'HH:mm')}
                    </div>
                  </div>
                ))}
                {publishes.length > 3 && (
                  <div className="text-xs text-gray-400 text-center">
                    +{publishes.length - 3} more
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Date Details */}
      {selectedDate && (
        <div className="mt-6 p-4 bg-gray-900 rounded-lg">
          <h3 className="text-lg font-semibold mb-3">
            {format(selectedDate, 'MMMM d, yyyy')} - {getPublishesForDate(selectedDate).length} scheduled
          </h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {getPublishesForDate(selectedDate).map(pub => (
              <div key={pub.id} className="p-3 bg-gray-800 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Clock className="w-4 h-4 text-blue-400" />
                    <span className="font-semibold">{format(new Date(pub.scheduled_time), 'HH:mm')}</span>
                    <span>{pub.title}</span>
                  </div>
                  <div className="flex gap-1">
                    {pub.platforms.map(p => (
                      <span key={p} className="px-2 py-1 bg-blue-600 bg-opacity-30 rounded text-xs">
                        {p}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Schedule Modal */}
      {showScheduleModal && (
        <SchedulePublishModal
          accounts={accounts}
          onClose={() => setShowScheduleModal(false)}
          onSuccess={() => {
            setShowScheduleModal(false);
            fetchScheduledPublishes();
            onSchedule();
          }}
          preselectedDate={selectedDate}
        />
      )}
    </div>
  );
};

// Separate modal component for scheduling
interface SchedulePublishModalProps {
  accounts: any[];
  onClose: () => void;
  onSuccess: () => void;
  preselectedDate: Date | null;
}

const SchedulePublishModal: React.FC<SchedulePublishModalProps> = ({
  accounts,
  onClose,
  onSuccess,
  preselectedDate
}) => {
  const [formData, setFormData] = useState({
    account_id: '',
    video_path: '',
    title: '',
    description: '',
    platforms: [] as string[],
    scheduled_date: preselectedDate ? format(preselectedDate, 'yyyy-MM-dd') : format(new Date(), 'yyyy-MM-dd'),
    scheduled_time: '12:00',
    priority: 5
  });

  const handleSubmit = async () => {
    try {
      const scheduledDateTime = new Date(`${formData.scheduled_date}T${formData.scheduled_time}`);

      await fetch(apiUrl('/api/publishing/publish/scheduled'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          account_id: formData.account_id,
          platforms: formData.platforms,
          video_path: formData.video_path,
          title: formData.title,
          description: formData.description,
          scheduled_time: scheduledDateTime.toISOString(),
          priority: formData.priority,
          max_retries: 3
        })
      });

      onSuccess();
    } catch (error) {
      console.error('Schedule error:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h3 className="text-2xl font-bold mb-6">Schedule Publish</h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm mb-2">Account</label>
              <select
                value={formData.account_id}
                onChange={(e) => setFormData({ ...formData, account_id: e.target.value })}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
              >
                <option value="">Select account</option>
                {accounts.map((acc: any) => (
                  <option key={acc.account_id} value={acc.account_id}>{acc.account_id}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm mb-2">Video Path</label>
              <input
                type="text"
                value={formData.video_path}
                onChange={(e) => setFormData({ ...formData, video_path: e.target.value })}
                placeholder="/path/to/video.mp4"
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm mb-2">Title</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Video title"
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm mb-2">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Video description"
                rows={3}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm mb-2">Platforms</label>
              <div className="grid grid-cols-2 gap-2">
                {['tiktok', 'instagram', 'facebook', 'linkedin', 'youtube'].map(platform => (
                  <label key={platform} className="flex items-center space-x-2 p-2 bg-gray-800 rounded cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.platforms.includes(platform)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setFormData({ ...formData, platforms: [...formData.platforms, platform] });
                        } else {
                          setFormData({ ...formData, platforms: formData.platforms.filter(p => p !== platform) });
                        }
                      }}
                    />
                    <span className="capitalize">{platform}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm mb-2">Date</label>
                <input
                  type="date"
                  value={formData.scheduled_date}
                  onChange={(e) => setFormData({ ...formData, scheduled_date: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm mb-2">Time</label>
                <input
                  type="time"
                  value={formData.scheduled_time}
                  onChange={(e) => setFormData({ ...formData, scheduled_time: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm mb-2">Priority (1-10)</label>
              <input
                type="range"
                min="1"
                max="10"
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
                className="w-full"
              />
              <div className="text-center text-sm text-gray-400">Priority: {formData.priority}</div>
            </div>
          </div>

          <div className="flex justify-end space-x-3 mt-6">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={!formData.account_id || !formData.video_path || !formData.title || formData.platforms.length === 0}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Schedule
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PublishingCalendar;
