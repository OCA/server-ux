/** @odoo-module **/
import {
    condition,
    connector,
    domainFromTree,
    formatValue,
    normalizeValue,
    treeFromDomain,
} from "@web/core/tree_editor/condition_tree";
import {deserializeDateTime, serializeDate} from "@web/core/l10n/dates";

function findDateRange(dateRanges, value, type) {
    if (!value.every((v) => typeof v === "string")) {
        return undefined;
    }
    const [dateEnd, dateStart] =
        type === "date"
            ? value
            : value.map((v) => serializeDate(deserializeDateTime(v)));
    return dateRanges.find(
        (range) => range.date_end === dateEnd && range.date_start === dateStart
    );
}

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

function createDateRangeOperators(tree, options) {
    if (["condition", "complex_condition"].includes(tree.type)) {
        return tree;
    }
    const processedChildren = tree.children.map((child) =>
        createDateRangeOperators(child, options)
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
            const fieldDef = options.getFieldDef(child1.path);
            const range =
                ["date", "datetime"].includes(fieldDef?.type) &&
                findDateRange(
                    options.dateRanges,
                    [child1.value, child2.value],
                    fieldDef.type
                );
            if (range) {
                children.push(
                    condition(
                        child1.path,
                        `daterange_${range.type_id[0]}`,
                        normalizeValue([child1.value, child2.value])
                    )
                );
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

/**
 * The domain does not keep whether the generic "daterange" operator was used:
 * restore it from the previous tree when the condition did not change.
 */
export function restoreDateRangeOperators(tree, previousTree) {
    if (!previousTree || tree.type !== previousTree.type) {
        return;
    }
    if (tree.type === "condition") {
        if (
            previousTree.operator === "daterange" &&
            tree.operator.startsWith?.("daterange_") &&
            formatValue(tree.path) === formatValue(previousTree.path) &&
            formatValue(tree.value) === formatValue(previousTree.value)
        ) {
            tree.operator = "daterange";
        }
    } else if (tree.children?.length === previousTree.children.length) {
        tree.children.forEach((child, i) =>
            restoreDateRangeOperators(child, previousTree.children[i])
        );
    }
}

export function domainFromTreeDateRange(tree) {
    return domainFromTree(removeDateRangeOperators(tree));
}

export function treeFromDomainDateRange(domain, options = {}) {
    return createDateRangeOperators(treeFromDomain(domain, options), options);
}
