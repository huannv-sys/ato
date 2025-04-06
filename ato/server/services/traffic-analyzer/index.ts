// Module phân tích lưu lượng mạng
import * as parserModule from './parser.js';
import * as visualizerModule from './visualizer.js';

const parser = parserModule.parser;
const visualizer = visualizerModule.visualizer;

export const trafficAnalyzer = {
  initialize: () => {
    console.log('Traffic analyzer initialized');
  },
  
  parseTrafficData: (data: any) => {
    return parser.parseData(data);
  },
  
  visualizeTraffic: (data: any) => {
    return visualizer.createChart(data);
  },
  
  getTopTalkers: (limit = 10) => {
    return Array(limit).fill(null).map((_, i) => ({
      ip: `192.168.1.${i + 1}`,
      hostname: `device-${i + 1}`,
      trafficIn: Math.floor(Math.random() * 1000),
      trafficOut: Math.floor(Math.random() * 1000)
    }));
  }
};