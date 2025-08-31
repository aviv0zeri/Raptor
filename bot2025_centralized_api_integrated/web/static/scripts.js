document.addEventListener('DOMContentLoaded', function () {
  class LogManager {
    constructor() {
      this.lastStoplossData = {
        currentPrice: null,
        highestLimit: null,
        timestamp: null
      };
      this.lastDetailsMessageId = null;
      this.init();
    }

    init() {
      this.startFetchingLogs();
    }

    // Format a timestamp into a readable string
    formatTimestamp(timestamp) {
      const isSeconds = timestamp.toString().length === 10;
      if (isSeconds) {
        timestamp *= 1000;
      }

      const date = new Date(timestamp);

      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');
      const milliseconds = String(date.getMilliseconds()).padStart(3, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();

      return `${hours}:${minutes}:${seconds}:${milliseconds} - ${day}/${month}/${year}`;
    }

    // Replace the data in the Stoploss log box
    replaceStoplossData(logBoxId, data, dataType) {
      if (this.lastStoplossData[dataType] === data) return;
      this.lastStoplossData[dataType] = data;

      const logBox = document.getElementById(logBoxId);
      if (logBox) {
        const dataDiv = logBox.querySelector(`#logBox-${dataType}`);

        if (dataDiv) {
          let dataSpan = dataDiv.querySelector('.log-data');
          if (!dataSpan) {
            dataSpan = document.createElement('span');
            dataSpan.classList.add('log-data');
            dataDiv.appendChild(dataSpan);
          }

          if (dataType === 'timestamp') {
            data = this.formatTimestamp(data);
          }

          dataSpan.textContent = data;
        } else {
          console.error(`#logBox-${dataType} not found inside ${logBoxId}`);
        }
      } else {
        console.error(`Element with ID ${logBoxId} not found`);
      }
    }

    prependDetailsMessage(logBoxId, message, id) {
      if (id === this.lastDetailsMessageId) {
        console.log(`Duplicate message skipped for ID: ${id}`);
        return; // Skip if the message ID is the same as the last one
      }

      this.lastDetailsMessageId = id;

      const logBox = document.getElementById(logBoxId);
      if (logBox) {
        const detailsBox = logBox.querySelector('#logBox-details');
        if (detailsBox) {
          // Create a new div for each log entry
          const newMessageDiv = document.createElement('div');
          newMessageDiv.classList.add('log-data'); // Optional: add a class for styling
          newMessageDiv.textContent = message;

          // Find the <h2> element and insert the new message after it
          const header = detailsBox.querySelector('h2');
          if (header) {
            detailsBox.insertBefore(newMessageDiv, header.nextSibling);
          } else {
            console.error('No <h2> element found inside #logBox-details.');
          }
        } else {
          console.error(`#logBox-details not found inside ${logBoxId}`);
        }
      } else {
        console.error(`Element with ID ${logBoxId} not found`);
      }
    }

    // Fetch log data from the backend API using Axios with async/await
    async fetchLogData(logBoxId, apiUrl) {
      try {
        const response = await axios.get(apiUrl);

        if (response.data.length > 0) {
          const newData = response.data[response.data.length - 1];

          if (logBoxId === 'logBox1') {
            this.replaceStoplossData(
              'logBox1',
              newData.current_price,
              'currentprice'
            );
            this.replaceStoplossData(
              'logBox1',
              newData.highest_limit,
              'pricelimit'
            );
            this.replaceStoplossData('logBox1', newData.timestamp, 'timestamp');
          } else if (logBoxId === 'logBox2') {
            this.prependDetailsMessage('logBox2', newData.message, newData.id);
          }
        }
      } catch (error) {
        console.error(`Error fetching log data for ${logBoxId}:`, error);
      }
    }

    // Start periodic fetching of logs
    startFetchingLogs() {
      setInterval(() => {
        this.fetchLogData('logBox1', '/get_logs_stoploss');
        this.fetchLogData('logBox2', '/get_logs_details');
      }, 1000);
    }
  }

  // Initialize the LogManager
  new LogManager();
});
