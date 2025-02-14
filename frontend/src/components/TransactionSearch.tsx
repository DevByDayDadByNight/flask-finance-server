import React from "react";
import TransactionList from "./TransactionList";
import { getTransactions } from "../api";
import { formatDate } from "../utils";
import TransactionFilter from "./TransactionFilter";

interface Transaction {
    id: number;
    amount: number;
    category?: string;
    postDate: string;
    description: string;
}

export default function TransactionSearch() {

    const [transactions, setTransactions] = React.useState<Transaction[]>([]);
    const [startDate, setStartDate] = React.useState("");
    const [endDate, setEndDate] = React.useState("");
    const [selectedCategories, setSelectedCategories] = React.useState<string[]>([]);

    const handleSearch = async (sd?: string, ed?: string) => {
        if(!sd || !ed) return;
        const response = await getTransactions(startDate, endDate);
        setTransactions(response.data);
    }

    const txnUpdated = (txn: Transaction) => {
        const newTxns = transactions.map((tx) =>
          tx.id === txn.id ? txn : tx
        )
        setTransactions(newTxns);
      }



    return (
        <div>
            <h1>Transaction Search</h1>

            <div>
                <label>
                    Start Date:
                    <input
                        type="date"
                        name="startDate"
                        value={startDate}
                        onChange={(e) => { 
                            const date = formatDate(e.target.value);
                            setStartDate(date);
                            handleSearch(date, endDate);
                        }}
                    />
                </label>
            </div>
            <div>
                <label>
                    End Date:
                    <input
                        type="date"
                        name="endDate"
                        value={endDate}
                        onChange={(e) => { 
                            const date = formatDate(e.target.value);
                            setEndDate(date);
                            handleSearch(startDate, date);
                        }}
                    />
                </label>
            </div>

            <TransactionFilter
                transactions={transactions}
                selectedCategories={selectedCategories}
                onChange={(cats: string[]) => setSelectedCategories(cats)}
            />

            <TransactionList
                txns={transactions.filter((txn) => selectedCategories.length === 0 || selectedCategories.includes(txn.category || ""))}
                onUpdated={(txn: Transaction) => { txnUpdated(txn) }}
            />
        </div>
    );
}
