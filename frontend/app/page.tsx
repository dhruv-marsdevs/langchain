"use client";

import { useState } from "react";
import Chart from "./components/Charts";

import CircleLoader from "react-spinners/CircleLoader";

export default function Home() {
	const [data, setData] = useState([]);
	const [answer, setAnswer] = useState("");
	const [question, setQuestion] = useState("");
	const [isLoading, setIsLoading] = useState(false);

	const handleSubmitClick = async () => {
		setIsLoading(true);
		setAnswer("");
		const response = await fetch("http://localhost:5000/query", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ question: question }),
		});

		if (!response.ok) {
			setIsLoading(false);
			return;
		}

		const data = await response.json();
		setIsLoading(false);
		const dataPoints = data?.result?.chart_data?.map((val: any) => {
			return {
				...val,
				date: new Date(val.date),
			};
		});
		console.log("dataPoints", dataPoints);

		setData(dataPoints);
		setAnswer(data?.result?.answer);
		setQuestion("");
	};

	const options = {
		data: data,
		title: {
			text: `AAPL Stock Price`,
		},
		subtitle: {
			text: "Candlestick Chart",
		},
		footnote: {
			text: "",
		},
		series: [
			{
				type: "candlestick",
				xKey: "date",
				xName: "Date",
				lowKey: "low",
				highKey: "high",
				openKey: "open",
				closeKey: "close",
			},
		],
	};

	const contentRender = () => {
		if (!answer && isLoading) {
			return <CircleLoader color="#3b82f6" />;
		} else if (answer) {
			return answer;
		} else {
			return null;
		}
	};

	return (
		<div className="flex flex-col gap-4 h-full p-4">
			<div className="border h-5/6 rounded-lg p-4">
				<Chart options={options} />
				<div className="items-left justify-center flex mt-4 pt-2">
					{contentRender()}
				</div>
			</div>
			<div className="h-1/6">
				<div className="flex gap-2 w-full items-center">
					<div className="w-full flex gap-2">
						<input
							type="text"
							name="query"
							id="query"
							className="rounded-lg w-full p-2 border items-center flex justify-center"
							onChange={(e) => {
								setQuestion(e.target.value);
							}}
							value={question}
							onKeyDown={(e) => {
								if (e.key === "Enter") {
									handleSubmitClick();
								}
							}}
						/>
						<input
							type="button"
							value={`${isLoading ? "Loading..." : "Submit"}`}
							className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg"
							style={{
								opacity: isLoading ? 0.5 : 1,
								cursor:
									isLoading || !question
										? "not-allowed"
										: "pointer",
							}}
							onClick={handleSubmitClick}
						/>
					</div>
				</div>
			</div>
		</div>
	);
}
