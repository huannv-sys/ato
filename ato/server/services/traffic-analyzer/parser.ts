// Parser cho dữ liệu lưu lượng

export const parser = {
  parseData: (data: any) => {
    console.log('Parsing traffic data:', data);
    return {
      parsed: true,
      timestamp: new Date(),
      data: data
    };
  },
  
  extractMetrics: (data: any) => {
    return {
      bytesIn: data?.bytesIn || 0,
      bytesOut: data?.bytesOut || 0,
      packetsIn: data?.packetsIn || 0,
      packetsOut: data?.packetsOut || 0
    };
  }
};