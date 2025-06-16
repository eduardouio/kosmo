// Box size hierarchy: FB (Full Box) → HB (Half Box) → QB (Quarter Box) → EB (Eighth Box)
// Conversion ratios:
// - 1 FB = 2 HB
// - 1 HB = 2 QB
// - 1 QB = 2 EB

export const BOX_SIZES = {
    FB: { name: 'FB', down: 'HB', up: null, ratio: 1 },
    HB: { name: 'HB', down: 'QB', up: 'FB', ratio: 2 },
    QB: { name: 'QB', down: 'EB', up: 'HB', ratio: 4 },
    EB: { name: 'EB', down: null, up: 'QB', ratio: 8 }
};

export const canSplit = (boxModel) => {
    return BOX_SIZES[boxModel]?.down !== null;
};

export const canMerge = (boxModel, selectedCount = 1, itemQuantity = 1) => {
    // Can merge if there's a larger box size and either:
    // 1. We have 2 or more items selected, or
    // 2. We have exactly 1 item with quantity >= 2
    const hasLargerSize = BOX_SIZES[boxModel]?.up !== null;
    const hasEnoughToMerge = selectedCount >= 2 || (selectedCount === 1 && itemQuantity >= 2);
    return hasLargerSize && hasEnoughToMerge;
};

export const getMergeTarget = (boxModel) => {
    return BOX_SIZES[boxModel]?.up;
};

export const getSplitTarget = (boxModel) => {
    return BOX_SIZES[boxModel]?.down;
};

export const splitStems = (stems) => {
    // When splitting, we divide the stems between two boxes
    // For odd numbers, first box gets the extra stem
    return {
        first: Math.ceil(stems / 2),
        second: Math.floor(stems / 2)
    };
};

/**
 * Calculate how many boxes of target size we get when splitting
 * @param {string} boxModel - Current box model
 * @param {number} quantity - Current quantity
 * @returns {number} - Number of smaller boxes
 */
export const getSplitQuantity = (boxModel, quantity) => {
    // When splitting, we get double the quantity of smaller boxes
    return quantity * 2;
};

/**
 * Calculate how many boxes of target size we get when merging
 * @param {string} boxModel - Current box model
 * @param {number} quantity - Current quantity
 * @returns {number} - Number of larger boxes
 */
export const getMergeQuantity = (boxModel, quantity) => {
    // When merging, we get half the quantity of larger boxes
    return Math.floor(quantity / 2);
};

/**
 * Calculate remaining boxes after merge
 * @param {string} boxModel - Current box model
 * @param {number} quantity - Current quantity
 * @returns {number} - Remaining boxes
 */
export const getRemainingAfterMerge = (boxModel, quantity) => {
    return quantity % 2;
};
