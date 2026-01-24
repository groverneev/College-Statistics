"use client";

import { CostsData } from "@/lib/types";
import { formatCurrency } from "@/utils/dataHelpers";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  Legend,
} from "recharts";

interface CostsChartProps {
  data: CostsData;
  schoolColor?: string;
}

export default function CostsChart({
  data,
  schoolColor = "#4E3629",
}: CostsChartProps) {
  const chartData = [
    {
      name: "Cost of Attendance",
      tuition: data.tuition,
      fees: data.fees,
      roomAndBoard: data.roomAndBoard,
    },
  ];

  const COLORS = {
    tuition: schoolColor,
    fees: `${schoolColor}99`,
    roomAndBoard: `${schoolColor}55`,
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Cost of Attendance</h3>

      <div className="text-center mb-4">
        <div className="text-3xl font-bold" style={{ color: schoolColor }}>
          {formatCurrency(data.totalCOA)}
        </div>
        <div className="text-sm text-gray-500">Total Annual Cost</div>
      </div>

      <div className="h-24 mb-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical">
            <XAxis type="number" hide />
            <YAxis type="category" dataKey="name" hide />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-white p-2 border border-gray-200 rounded shadow-sm">
                      {payload.map((entry, index) => (
                        <p key={index} className="text-sm">
                          {entry.name}: {formatCurrency(entry.value as number)}
                        </p>
                      ))}
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar
              dataKey="tuition"
              stackId="a"
              fill={COLORS.tuition}
              name="Tuition"
              radius={[4, 0, 0, 4]}
            />
            <Bar
              dataKey="fees"
              stackId="a"
              fill={COLORS.fees}
              name="Fees"
            />
            <Bar
              dataKey="roomAndBoard"
              stackId="a"
              fill={COLORS.roomAndBoard}
              name="Room & Board"
              radius={[0, 4, 4, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-3 gap-2 text-center text-sm">
        <div className="p-2 rounded" style={{ backgroundColor: `${schoolColor}15` }}>
          <div className="font-semibold">{formatCurrency(data.tuition)}</div>
          <div className="text-gray-500 text-xs">Tuition</div>
        </div>
        <div className="p-2 rounded" style={{ backgroundColor: `${schoolColor}10` }}>
          <div className="font-semibold">{formatCurrency(data.fees)}</div>
          <div className="text-gray-500 text-xs">Fees</div>
        </div>
        <div className="p-2 rounded" style={{ backgroundColor: `${schoolColor}08` }}>
          <div className="font-semibold">{formatCurrency(data.roomAndBoard)}</div>
          <div className="text-gray-500 text-xs">Room & Board</div>
        </div>
      </div>
    </div>
  );
}
