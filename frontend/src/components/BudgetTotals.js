import React, { useEffect, useState } from "react";


const BudgetTotals = ({ txns, lineItems, selectedBudget }) => {

     const [totals, setTotals] = useState({});
     const [budget, setBudget] = useState({});

     useEffect(() => {
        setBudget(selectedBudget);
        calculateTotals(txns, lineItems);
    
     }, [txns, lineItems, selectedBudget]);

     const calculateTotals = (transactions, lineItems) => {
        console.log("hereeee")
        const varActMap = calculateTotalForAType("Variable", transactions, lineItems);
        console.log("done")
        console.log(varActMap)
        const varActTotal = Object.values(varActMap).reduce((sum, value) => sum + value, 0);
        console.log("varActTotal", varActTotal)
        const notRecordedMap = calculateTotalForAType("NotCounted", transactions, lineItems);
        console.log("notRecordedMap", notRecordedMap)
        const incomeTotal = lineItems.filter((x) => x.type === "Income").reduce((sum, item) => sum + item.amount, 0);
        console.log("incomeTotal", incomeTotal)
        const fixedTotal = lineItems.filter((x) => x.type === "Fixed").reduce((sum, item) => sum + item.amount, 0);
        const varTotal = lineItems.filter((x) => x.type === "Variable").reduce((sum, item) => sum + item.amount, 0);
        const budTot = incomeTotal - fixedTotal - varTotal
    
        const budAct = incomeTotal - fixedTotal - (varActTotal * -1)
    
        const mergedMap = { ...varActMap, ...notRecordedMap };
        console.log("mergedMap", mergedMap)
    
        console.log(`income: ${incomeTotal}`)
        console.log(`fixed: ${fixedTotal}`)
        console.log(`budT: ${budTot}`)
        console.log(`budAct: ${budAct}`)
    
        setTotals({
          budgetTotal: budTot,
          budgetActual: budAct,
          catTotal: mergedMap
        })
    
      };

       function calculateTotalForAType(type, transactions, lineItems) {
          try {
      
            // Step 1: Filter line items by the specified type and create a map of category mappings
            const categoryMap = lineItems
              .filter((item) => item.type === type)
              .reduce((acc, item) => {
                acc[item.name.toLowerCase()] = item.related_categories.map((cat) =>
                  cat.toLowerCase()
                );
                return acc;
              }, {});
      
            // Step 2: Flatten the list of all related categories
            const allCategories = Object.values(categoryMap).flat();
      
            // Step 3: Group transactions by category and calculate sums
            const totalsNotCombined = transactions.reduce((acc, txn) => {
              const lowerCategory = txn.category.toLowerCase();
              if (allCategories.includes(lowerCategory)) {
                acc[lowerCategory] = (acc[lowerCategory] || 0) + txn.amount;
              }
              return acc;
            }, {});
      
            // Step 4: Map line items to their calculated totals
            return Object.entries(categoryMap).reduce((acc, [key, relatedCategories]) => {
              acc[key] = relatedCategories.reduce(
                (sum, cat) => sum + (totalsNotCombined[cat] || 0),
                0
              );
              return acc;
            }, {});
          } catch (error) {
            console.error("Error calculating totals for a type:", error);
            return {};
          }
      
        }

        function daysPassed(lesserDate, greaterDate) {
            
            // Calculate the difference in milliseconds
            const difference = lesserDate - greaterDate;
            
            // Convert milliseconds to days
            return Math.floor(difference / (1000 * 60 * 60 * 24));
        }

        const spends = (spendBudgeted, spendActual) => {
            const daysPassedSince = daysPassed(new Date(budget.start_date), new Date()) * -1;
            const daysRemaining = daysPassed(new Date(), new Date(budget.end_date)) * -1;
            
            const dailySpend = (spendActual / daysPassedSince) * -1;
            const projectedRemaining = (spendBudgeted - dailySpend * daysRemaining);
            const projectedTotal = dailySpend * (daysPassedSince + daysRemaining);

            return (
                <div>
                    <p>Days Passed: {daysPassedSince}</p>
                    <p>Days Remaining: {daysRemaining}</p>
                    <p>Budgeted Daily Spend: {spendBudgeted / (daysPassedSince + daysRemaining)}</p>
                    <p>Daily Spend: {dailySpend}</p>
                    <p>Projected Remaining: {projectedRemaining}</p>
                    <p>Projected Total Spend: {projectedTotal}</p>
                </div>
            )
        }

      


        return (
            <div>
                  <table className="line-item-table">
                            <thead>
                              <tr>
                                <th>Name</th>
                                <th>Budgeted</th>
                                <th></th>
                                <th>Actual</th>
                              </tr>
                            </thead>
                            <tbody>
                              {lineItems.map((item) => (
                                <tr>
                                  <td>{item.name}</td>
                                  <td>{item.amount}</td>
                                  <td></td>
                                  <td>{
                
                                  totals.catTotal?.[item.name] ?? item.amount
                
                
                                  }</td>
                                  
                                </tr>
                              ))}
                              <tr>
                                <td>Budgeted</td>
                                <td>{totals.budgetTotal}</td>
                                <td>Actual</td>
                                <td>{totals.budgetActual}</td>
                              </tr>
                            </tbody>
                          </table>

                          {
                            spends(lineItems.find(item => item.name === "spend")?.amount, totals.catTotal?.["spend"])
                          }
                
            </div>
        )

};
export default BudgetTotals;
