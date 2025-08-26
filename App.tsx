import React, { useState } from 'react';
import * as XLSX from 'xlsx';
import Plot from 'react-plotly.js';
import { Table, Select } from 'antd';

type Row = { [key: string]: any };

const App: React.FC = () => {
  const [data, setData] = useState<Row[]>([]);
  const [users, setUsers] = useState<string[]>([]);
  const [selectedUser, setSelectedUser] = useState<string>();
  const [categoryCounts, setCategoryCounts] = useState<any[]>([]);
  const [channelCounts, setChannelCounts] = useState<any[]>([]);
  const [storeCounts, setStoreCounts] = useState<any[]>([]);
  const [top5Cat, setTop5Cat] = useState<any[]>([]);
  const [top5Channel, setTop5Channel] = useState<any[]>([]);
  const [top5Store, setTop5Store] = useState<any[]>([]);

  // 파일 업로드 및 파싱
  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      const bstr = evt.target?.result;
      const wb = XLSX.read(bstr, { type: 'binary' });
      const wsname = wb.SheetNames[0];
      const ws = wb.Sheets[wsname];
      const jsonData: Row[] = XLSX.utils.sheet_to_json(ws);
      setData(jsonData);
      // 사용자 목록 추출
      const userList = Array.from(new Set(jsonData.map(row => row['이름']))).filter(Boolean);
      setUsers(userList as string[]);
      setSelectedUser(undefined);
    };
    reader.readAsBinaryString(file);
  };

  // 사용자 선택 시 집계
  React.useEffect(() => {
    if (!selectedUser || data.length === 0) return;
    const userData = data.filter(row => row['이름'] === selectedUser);
    // 카테고리별
    const catMap: { [key: string]: number } = {};
    userData.forEach(row => {
      const cat = row['카테고리'];
      catMap[cat] = (catMap[cat] || 0) + 1;
    });
    const catArr = Object.entries(catMap).map(([k, v]) => ({ name: k, value: v }));
    setCategoryCounts(catArr);
    setTop5Cat(catArr.sort((a, b) => b.value - a.value).slice(0, 5));
    // 결제채널별
    const chMap: { [key: string]: number } = {};
    userData.forEach(row => {
      const ch = row['결제채널'];
      chMap[ch] = (chMap[ch] || 0) + 1;
    });
    const chArr = Object.entries(chMap).map(([k, v]) => ({ name: k, value: v }));
    setChannelCounts(chArr);
    setTop5Channel(chArr.sort((a, b) => b.value - a.value).slice(0, 5));
    // 매장명별
    const stMap: { [key: string]: number } = {};
    userData.forEach(row => {
      const st = row['매장명'];
      stMap[st] = (stMap[st] || 0) + 1;
    });
    const stArr = Object.entries(stMap).map(([k, v]) => ({ name: k, value: v }));
    setStoreCounts(stArr);
    setTop5Store(stArr.sort((a, b) => b.value - a.value).slice(0, 5));
  }, [selectedUser, data]);

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 24 }}>
      <h2>엑셀 영수증 분석 대시보드 (React Only)</h2>
      <input type="file" accept=".xlsx" onChange={handleFile} />
      {users.length > 0 && (
        <div style={{ margin: '16px 0' }}>
          <Select
            style={{ width: 200 }}
            placeholder="사용자 선택"
            value={selectedUser}
            onChange={setSelectedUser}
            options={users.map(u => ({ label: u, value: u }))}
          />
        </div>
      )}
      {selectedUser && (
        <>
          <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
            <div>
              <Plot
                data={[{
                  type: 'pie',
                  labels: categoryCounts.map(c => c.name),
                  values: categoryCounts.map(c => c.value),
                  hole: 0.5,
                }]}
                layout={{ title: '카테고리별', width: 300, height: 300 }}
                config={{ displayModeBar: false }}
              />
              <Table
                dataSource={top5Cat.map((row, i) => ({ ...row, key: i + 1 }))}
                columns={[
                  { title: 'No', dataIndex: 'key', align: 'center' },
                  { title: '카테고리', dataIndex: 'name', align: 'center' },
                  { title: '건수', dataIndex: 'value', align: 'center' }
                ]}
                pagination={false}
                size="small"
                style={{ marginTop: 8 }}
              />
            </div>
            <div>
              <Plot
                data={[{
                  type: 'pie',
                  labels: channelCounts.map(c => c.name),
                  values: channelCounts.map(c => c.value),
                  hole: 0.5,
                }]}
                layout={{ title: '결제채널별', width: 300, height: 300 }}
                config={{ displayModeBar: false }}
              />
              <Table
                dataSource={top5Channel.map((row, i) => ({ ...row, key: i + 1 }))}
                columns={[
                  { title: 'No', dataIndex: 'key', align: 'center' },
                  { title: '결제채널', dataIndex: 'name', align: 'center' },
                  { title: '건수', dataIndex: 'value', align: 'center' }
                ]}
                pagination={false}
                size="small"
                style={{ marginTop: 8 }}
              />
            </div>
            <div>
              <Plot
                data={[{
                  type: 'pie',
                  labels: storeCounts.map(c => c.name),
                  values: storeCounts.map(c => c.value),
                  hole: 0.5,
                }]}
                layout={{ title: '매장명별', width: 300, height: 300 }}
                config={{ displayModeBar: false }}
              />
              <Table
                dataSource={top5Store.map((row, i) => ({ ...row, key: i + 1 }))}
                columns={[
                  { title: 'No', dataIndex: 'key', align: 'center' },
                  { title: '매장명', dataIndex: 'name', align: 'center' },
                  { title: '건수', dataIndex: 'value', align: 'center' }
                ]}
                pagination={false}
                size="small"
                style={{ marginTop: 8 }}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default App;
