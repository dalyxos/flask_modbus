import React, { useEffect, useState } from 'react';
import { Row, Col, Statistic, Card } from 'antd';
import { hot } from 'react-hot-loader/root';

const StatusPanel = () => {
  const load = 10;
  const circuitBreaker = false;
  const powerMeter = { current: 0, power: 0, voltage: 0 };
  /*const [load, setLoad] = useState(0)
  const [circuitBreaker, setCircuitBreaker] = useState(false);
  const [powerMeter, setPowerMeter] = useState({ current: 0, power: 0, voltage: 0 });

  const fetchData = () => {
    fetch('/load').then(res => res.json()).then(data => {
      setLoad(data.load);
    });

    fetch('/circuit-breaker').then(res => res.json()).then(data => {
      setCircuitBreaker(data.circuitBreaker);
    });

    fetch('/power-meter').then(res => res.json()).then(data => {
      setPowerMeter(data.powerMeter);
    });
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);

    return () => clearInterval(interval);
  }, []);*/

  return (
    <Row gutter={16}>
      <Col span={12}>
        <Card title="Load">
          <Statistic title="Current" value={load} suffix='A' precision={2} />
        </Card>
      </Col>
      <Col span={12}>
        <Card title="Circuit Breaker">
          <Statistic value={circuitBreaker ? 'On' : 'Off'} valueStyle={{ color: circuitBreaker ? 'green' : 'red' }} />
        </Card>
      </Col>
      <Col span={12}>
        <Card title="Power Meter">
          <Statistic title="Total Current" value={powerMeter.current} suffix='A' precision={2} />
          <br />
          <Statistic title="Total Power" value={powerMeter.power} suffix='W' precision={2} />
          <br />
          <Statistic title="Voltage" value={powerMeter.voltage} suffix='V' precision={2} />
        </Card>
      </Col>
    </Row>
  );
}

export default hot(StatusPanel);