// Visualizer cho dữ liệu lưu lượng

export const visualizer = {
  createChart: (data: any) => {
    console.log('Creating chart for traffic data:', data);
    return {
      type: 'linechart',
      title: 'Network Traffic',
      data: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        datasets: [
          {
            label: 'Traffic In',
            data: [65, 59, 80, 81, 56, 55, 40]
          },
          {
            label: 'Traffic Out',
            data: [28, 48, 40, 19, 86, 27, 90]
          }
        ]
      }
    };
  }
};