// creating a visualization of how blood type for a child is determined, given two blood-types.

document.getElementById("generateTree").addEventListener("click", function() {
    const parent1 = document.getElementById("parent1").value;
    const rh1 = document.getElementById("rh1").value;
    const parent2 = document.getElementById("parent2").value;
    const rh2 = document.getElementById("rh2").value;

    const childBloodTypes = getPossibleBloodTypes(parent1, rh1, parent2, rh2);

    const data = {
        name: "Blood Type Inheritance",
        children: [
            { name: `Parent 1: ${parent1}${rh1}` },
            { name: `Parent 2: ${parent2}${rh2}` },
            {
                name: "Possible Children Types",
                children: childBloodTypes.map(bt => ({ name: bt }))
            }
        ]
    };

    drawTree(data);
});

// getting the possible blood types and Rh antigens
function getPossibleBloodTypes(parent1, rh1, parent2, rh2) {

    // JS object to store k:v pairs, used like a dict. Here, we use them to store arrays of strings, which are, blood types mapped to Alleles
    const inheritanceMap = {
        "AA": ["A"], "AO": ["A", "O"],
        "BB": ["B"], "BO": ["B", "O"],
        "AB": ["A", "B", "AB"],
        "OO": ["O"]
    };

    // getting the allels when inputted by the user
    function getAlleles(bloodType) {
        if (bloodType === "AB") return ["A", "B"];
        if (bloodType === "O") return ["O", "O"];
        return [bloodType, "O"];
    }

    let alleles1 = getAlleles(parent1);
    let alleles2 = getAlleles(parent2);

    let children = new Set();
    for (let a1 of alleles1) {
        for (let a2 of alleles2) {
            let key1 = a1 + a2;
            let key2 = a2 + a1;
            // using the spread operator to expand an iterable like an array or a set into individual elements
            // the below line creates a new array that contains all the elements from children and inheritanceMap[key1]
            // this new array is then used to create a new set which is assigned to children
            // This way, we're adding all the elements from inheritanceMap[key1] to children.
            if (inheritanceMap[key1]) children = new Set([...children, ...inheritanceMap[key1]]);
            if (inheritanceMap[key2]) children = new Set([...children, ...inheritanceMap[key2]]);
        }
    }

    let rhChildren = new Set();
    if (rh1 === "+" || rh2 === "+") {
        rhChildren.add("+");
        if (rh1 === "-" && rh2 === "-") {
            rhChildren.add("-");
        }
    } else {
        rhChildren.add("-");
    }

    let finalChildren = [];
    children.forEach(bt => {
        rhChildren.forEach(rh => {
            finalChildren.push(bt + rh);
        });
    });

    return finalChildren;
}


// drawing the actual tree using the D3.js svg methods, in heirarchical layout mostly taken from the D3.js source with help from CS50.ai/ddb
// source https://d3js.org/d3-hierarchy/tree
function drawTree(data) {
    console.log("drawing tree");

    // reset explanation
    document.getElementById("explanation").innerHTML = "";

    d3.select("#tree-container").select("svg").remove();

    const width = window.innerWidth * 0.8;
    const height = window.innerHeight * 0.7;

    const svg = d3.select("#tree-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .style("background", "black")
        .append("g")
        .attr("transform", `translate(${width / 4}, 50)`);

    const treeLayout = d3.tree().size([width - 400, height - 200]);
    const root = d3.hierarchy(data);
    treeLayout(root);

    const allNodes = root.descendants();
    const allLinks = root.links();

    allNodes.forEach(d => d._visible = false);
    allLinks.forEach(d => d._visible = false);

    function revealNext(index) {
        if (index >= allNodes.length) return;

        const node = allNodes[index];
        node._visible = true;

        // line drawing logic to start from the outer boundary
        svg.selectAll("line")
            .data(allLinks.filter(l => l.source._visible && l.target._visible))
            .enter()
            .append("line")
            .attr("x1", function(d) {

                // calculate starting x position by considering the radius of the circle
                const angle = Math.atan2(d.target.y - d.source.y, d.target.x - d.source.x);
                return d.source.x + Math.cos(angle) * 18; // 18 is the radius of both circles
            })
            .attr("y1", function(d) {
                const angle = Math.atan2(d.target.y - d.source.y, d.target.x - d.source.x);
                return d.source.y + Math.sin(angle) * 18; // 18
            })
            .attr("x2", d => d.source.x)
            .attr("y2", d => d.source.y)
            .style("stroke", "#fff")
            .style("stroke-width", 2)
            .style("opacity", 0)
            .transition()
            .duration(800)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y)
            .style("opacity", 1);

        // nodes/links appending
        const nodeGroup = svg.append("g")
            .attr("class", "node")
            .attr("transform", `translate(${node.x},${node.y})`)
            .style("opacity", 0);

        // circles
        nodeGroup.append("circle")
            .attr("r", 18)
            .style("none", node.data.name.includes("A") || node.data.name.includes("B") ? "crimson" : "gold")
            .style("stroke", "#fff")
            .style("stroke-width", 2)
            .transition()
            .duration(600)
            .attr("r", 18);

        // text shown inside the circle
        nodeGroup.append("text")
            .attr("dy", "0")
            .attr("text-anchor", "middle")
            .style("fill", "white")
            .style("font-size", "16px")
            .style("font-weight", "bold")
            .style("opacity", 0)
            .text(node.data.name)  // display blood group
            .transition()
            .duration(800)
            .delay(300)
            .style("opacity", 1);

        // transition
        nodeGroup.transition()
            .duration(600)
            .style("opacity", 1);

        if (index > 1) {
            showExplanation(node.data.name);
        }

        setTimeout(() => revealNext(index + 1), 4000);
    }


    // explaining why the assignment of allels and Rh works the way it does ie, dominance/recessiveness of O type allele and +, - antigens
    function showExplanation(bloodType) {
        const explanationBox = document.getElementById("explanation");
        let message = "";

        if (bloodType.includes("O")) {
            message = `"O" is recessive, meaning it only appears if no dominant A or B is inherited.`;
        } else if (bloodType.includes("A") || bloodType.includes("B")) {
            message = `Blood types "A" and "B" are dominant, meaning they will be inherited if at least one parent carries them.`;
        } else if (bloodType.includes("+")) {
            message = `Rh+ is dominant, meaning a child will inherit it if at least one parent has it.`;
        } else {
            message = `"Rh-" is only inherited if both parents are Rh-.`;
        }

        explanationBox.innerHTML = `<p>${message}</p>`;
        explanationBox.style.opacity = 1;

    }

    revealNext(0);
}
