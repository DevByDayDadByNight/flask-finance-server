import { useEffect, useState } from "react";


const TransactionFilter = ({ transactions, selectedCategories, onChange }) => {
    const [availableCategories, setAvailableCategories] = useState([]);


    useEffect(() => {
        console.log("txns")
        console.log(transactions)
        // get all unique categories available in transactions
        const cats = transactions.map(txn => txn.category)
        const uniqueCats = [...new Set(cats)];
        setAvailableCategories(uniqueCats);
    }, [transactions])

    const onCatsChanged = (e) => {
        let cats;
        if (e.target.checked) {
            cats = [...selectedCategories, e.target.value]
        } else {
            cats = selectedCategories.filter(cat => cat !== e.target.value)
        }
        console.log(cats)
        onChange(cats);
    }




    return (
        <div className="transaction-filter">
            <p>Available Categories:</p>
            // use flex row
            <div style={{ display: "flex", flexDirection: "row", flexWrap: "wrap" }}>
                {
                    availableCategories.map((cat) => {
                        return (
                            <div key={cat} style={{ margin: "5px" }}>
                                <input type="checkbox" checked={selectedCategories.includes(cat)} value={cat} onChange={(e) => {
                                    onCatsChanged(e)
                                }} />
                                {cat ? cat : "Uncategorized"}
                            </div>
                        )
                    })
                }

            </div>

            <button onClick={() => {
                onChange([])
            }}>Clear</button>

            <button onClick={() => {
                onChange(availableCategories)
            }}>Select All</button>




        </div>
    )
}

export default TransactionFilter;