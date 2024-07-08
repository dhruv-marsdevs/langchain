import React, { useState } from "react";

import { AgCharts } from "ag-charts-react";
import "ag-charts-enterprise";

const Chart = ({ options }: { options: any }) => {
	return <AgCharts options={options} />;
};

export default Chart;
