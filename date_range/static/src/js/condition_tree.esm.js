import {
    condition,
    connector,
    formatValue,
    normalizeValue,
} from "@web/core/tree_editor/condition_tree";
import {domainFromTree} from "@web/core/tree_editor/domain_from_tree";
import {treeFromDomain} from "@web/core/tree_editor/tree_from_domain";

function addChild(parent, child) {
    if (child.type === "connector" && !child.negate && child.value === parent.value) {
        parent.children.push(...child.children);
    } else {
        parent.children.push(child);
    }
}

export function removeDateRangeOperators(tree) {
    if (tree.type === "complex_condition") {
        return tree;
    }
    if (tree.type === "condition") {
        if (!tree.operator.includes("daterange")) {
            return tree;
        }
        const {negate, path, value} = tree;
        return connector(
            "&",
            [condition(path, "<=", value[0]), condition(path, ">=", value[1])],
            negate
        );
    }
    const processedChildren = tree.children.map(removeDateRangeOperators);
    if (tree.value === "|") {
        return {...tree, children: processedChildren};
    }
    const newTree = {...tree, children: []};
    // After processing a child might have become a connector "&" --> normalize
    for (let i = 0; i < processedChildren.length; i++) {
        addChild(newTree, processedChildren[i]);
    }
    return newTree;
}

/**
 * Turns each "<=" / ">=" pair on the same field into a date range condition,
 * when getOperator returns an operator for it. A pair it does not recognize
 * is left untouched, so a hand-written interval is never replaced by a range.
 */
export function createDateRangeOperators(tree, getOperator = () => "daterange") {
    if (["condition", "complex_condition"].includes(tree.type)) {
        return tree;
    }
    const processedChildren = tree.children.map((child) =>
        createDateRangeOperators(child, getOperator)
    );
    if (tree.value === "|") {
        return {...tree, children: processedChildren};
    }
    const children = [];
    for (let i = 0; i < processedChildren.length; i++) {
        const child1 = processedChildren[i];
        const child2 = processedChildren[i + 1];
        if (
            child1.type === "condition" &&
            child2 &&
            child2.type === "condition" &&
            formatValue(child1.path) === formatValue(child2.path) &&
            child1.operator === "<=" &&
            child2.operator === ">="
        ) {
            const value = normalizeValue([child1.value, child2.value]);
            const operator = getOperator(child1.path, value);
            if (operator) {
                children.push(condition(child1.path, operator, value));
                i += 1;
                continue;
            }
        }
        children.push(child1);
    }
    if (children.length === 1) {
        return {...children[0]};
    }
    return {...tree, children};
}

export function domainFromTreeDateRange(tree) {
    return domainFromTree(removeDateRangeOperators(tree));
}

export function treeFromDomainDateRange(domain, options = {}) {
    return createDateRangeOperators(
        treeFromDomain(domain, options),
        options.getDateRangeOperator
    );
}
