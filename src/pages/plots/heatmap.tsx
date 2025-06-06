import React, { useState, useEffect, FC } from 'react';
import ReactDOM from 'react-dom';
import { Heatmap } from '@ant-design/plots';

const DemoHeatmap:FC<any> = ({data}) => {
//   const [data, setData] = useState([]);

//   useEffect(() => {
//     asyncFetch();
//   }, []);

//   const asyncFetch = () => {
//     fetch('https://gw.alipayobjects.com/os/bmw-prod/68d3f380-089e-4683-ab9e-4493200198f9.json')
//       .then((response) => response.json())
//       .then((json) => setData(json))
//       .catch((error) => {
//         console.log('fetch data failed', error);
//       });
//   };
//   const config = {
//     data,
//     xField: 'sample1',
//     yField: 'sample2',
//     colorField: 'value',
//     sizeField: 'value',
//     shapeField: 'square',
//     label: {
//       text: (d:any) => d.value,
//       position: 'inside',
//       style: {
//         fill: '#fff',
//         pointerEvents: 'none',
//       },
//     },
//     scale: {
//       size: { range: [12, 20] },
//       color: { range: ['#dddddd', '#9ec8e0', '#5fa4cd', '#2e7ab6', '#114d90'] },
//     },
//   };
  const config = {
    data,
    xField: 'sample1',
    yField: 'sample2',
    colorField: 'value',
    sizeField: 'value',
    shapeField: 'point',
    scale: {
      size: { range: [12, 20] },
      color: { range: ['#0d5fbb', '#7eadfc', '#fd8b6f', '#aa3523'] },
    },
    label: {
      text: (d:any) => d.value,
      position: 'inside',
      style: {
        fill: '#fff',
        shadowBlur: 2,
        shadowColor: 'rgba(0, 0, 0, .45)',
        pointerEvents: 'none',
      },
    },
  };

  return <Heatmap {...config} />;
};

export default DemoHeatmap 

// ReactDOM.render(<DemoHeatmap />, document.getElementById('container'));