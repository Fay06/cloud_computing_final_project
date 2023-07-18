const startDate = new Date(2022, 5, 1, 0, 0, 0);
const endDate = new Date(2023, 3, 20, 4, 0, 0);
const msPerMinute = 60 * 1000;

let currentDate = startDate;
let currentValue = 100;
const randomChange = () => (Math.random() - 0.5) * 0.5;

const sampleData = [];

while (currentDate <= endDate) {
  sampleData.push([currentDate.getTime(), currentValue]);
  currentDate = new Date(currentDate.getTime() + msPerMinute);
  currentValue += randomChange();
  currentValue = Math.round(currentValue * 100) / 100; // Round to 2 decimal places
}

function linearRegression(data) {
  const n = data.length;
  let sumX = 0;
  let sumY = 0;
  let sumXY = 0;
  let sumXX = 0;

  for (const point of data) {
    sumX += point[0];
    sumY += point[1];
    sumXY += point[0] * point[1];
    sumXX += point[0] * point[0];
  }

  const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
  const intercept = (sumY - slope * sumX) / n;

  return { slope, intercept };
}

// Calculate the predicted value for tomorrow
const { slope, intercept } = linearRegression(sampleData);
const tomorrow = new Date(sampleData[sampleData.length - 1][0] + 24 * 60 * 60 * 1000);
const tomorrowValue = slope * tomorrow.getTime() + intercept;

// Add the predicted data point to the sample data
const forecastedData = [...sampleData, [tomorrow.getTime(), tomorrowValue]];

// Define a custom theme
Highcharts.theme = {
  colors: ['#AAF4E4', '#f44336', '#4caf50', '#ffeb3b', '#ff9800', '#9c27b0', '#03a9f4'],
  chart: {
    backgroundColor: null,
    style: {
      fontFamily: 'Roboto, sans-serif',
    },
    animation: {
      duration: 1000,
    },
  },
  title: {
    style: {
      fontSize: '26px',
      fontWeight: '400',
      color: '#AAF4E4',
    },
  },
  subtitle: {
    style: {
      fontSize: '18px',
      fontWeight: '400',
      color: '#AAF4E4',
    },
  },
  tooltip: {
    borderWidth: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.85)',
    shadow: false,
    style: {
      fontSize: '14px',
      color: '#F0F0F0',
    },
  },
  legend: {
    itemStyle: {
      fontWeight: '400',
      fontSize: '16px',
    },
  },
  xAxis: {
    labels: {
      style: {
        color: '#6e6e70',
        fontSize: '14px',
      },
      },
      },
      yAxis: {
      labels: {
      style: {
      color: '#6e6e70',
      fontSize: '14px',
      },
      },
      },
      plotOptions: {
      series: {
      shadow: true,
      marker: {
      radius: 4,
      symbol: 'square',
      lineWidth: 2,
      },
      animation: {
      duration: 1000,
      },
      },
      candlestick: {
      lineColor: '#404048',
      },
      },
      };
      
      // Apply the custom theme
      Highcharts.setOptions(Highcharts.theme);
      
      Highcharts.stockChart('chart', {
      series: [
      {
      name: 'US Dollar',
      data: sampleData,
      lineWidth: 3,
      color: Highcharts.getOptions().colors[0],
      fillColor: {
      linearGradient: [0, 0, 0, 300],
      stops: [
      [0, Highcharts.getOptions().colors[0]],
      [1, Highcharts.color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')],
      ],
      },
      marker: {
      enabled: true,
      fillColor: Highcharts.getOptions().colors[0],
      lineColor: Highcharts.getOptions().colors[0],
      },
      tooltip: {
      valueDecimals: 2,
      },
      },
      {
      name: 'Forecast',
      data: [forecastedData[forecastedData.length - 1]],
      lineWidth: 0,
      color: Highcharts.getOptions().colors[1],
      marker: {
      enabled: true,
      fillColor: Highcharts.getOptions().colors[1],
      lineColor: Highcharts.getOptions().colors[1],
      radius: 6,
      },
      tooltip: {
      valueDecimals: 2,
      },
      },
      ],
      
      yAxis: {
      opposite: false,
      lineWidth: 1,
      lineColor: '#AAF4E4',
      gridLineColor: '#e5e5e5',
      labels: {
      align: 'left',
      x: 5,
      y: -3,
      },
      },
      
      xAxis: {
      lineColor: '#AAF4E4',
      tickColor: '#AAF4E4',
      type: 'datetime',
      labels: {
      style: {
      fontSize: '14px',
      },
      formatter: function () {
      return Highcharts.dateFormat('%e %b %Y', this.value);
      },
      },
      },
      
      navigator: {
      outlineColor: '#AAF4E4',
      maskFill: 'rgba(63, 81, 181, 0.5)',
      series: {
      color: '#AAF4E4',
      lineColor: '#AAF4E4',
      },
      handles: {
      backgroundColor: '#ffffff',
      borderColor: '#AAF4E4',
      },
      },
      
      scrollbar: {
      barBackgroundColor: '#AAF4E4',
      barBorderRadius: 7,
      barBorderWidth: 0,
      buttonBackgroundColor: '#ffffff',
      buttonBorderWidth: 0,
      buttonBorderRadius: 7,
      trackBackgroundColor: '#f5f5f5',
      trackBorderWidth: 1,
      trackBorderColor: '#AAF4E4',
      trackBorderRadius: 7,
      },
      
      tooltip: {
      headerFormat: '<span style="font-size: 18px; font-weight: 400;">{point.key}</span><br>',
      },
      });
