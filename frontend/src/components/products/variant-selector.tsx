/**
 * Variant Selector Component
 * 
 * Product variant selection with options.
 */
'use client';

import { useState, useEffect } from 'react';
import { clsx } from 'clsx';
import type { ProductVariant } from '@/types';

interface VariantSelectorProps {
    variants: ProductVariant[];
    onVariantChange?: (variant: ProductVariant | null) => void;
}

export function VariantSelector({ variants, onVariantChange }: VariantSelectorProps) {
    const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(
        variants[0] || null
    );

    // Extract unique option types (e.g., color, size)
    const optionTypes = getOptionTypes(variants);
    const [selectedOptions, setSelectedOptions] = useState<Record<string, string>>(() => {
        if (variants[0]) {
            return variants[0].options;
        }
        return {};
    });

    useEffect(() => {
        // Find matching variant based on selected options
        const matchingVariant = variants.find((variant) =>
            Object.entries(selectedOptions).every(
                ([key, value]) => variant.options[key] === value
            )
        );
        setSelectedVariant(matchingVariant || null);
        onVariantChange?.(matchingVariant || null);
    }, [selectedOptions, variants, onVariantChange]);

    const handleOptionSelect = (optionType: string, value: string) => {
        setSelectedOptions((prev) => ({
            ...prev,
            [optionType]: value,
        }));
    };

    return (
        <div className="space-y-4">
            {optionTypes.map((optionType) => {
                const values = getOptionValues(variants, optionType);

                return (
                    <div key={optionType}>
                        <h3 className="mb-2 text-sm font-semibold text-gray-900 capitalize">
                            {optionType}
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {values.map((value) => {
                                const isSelected = selectedOptions[optionType] === value;
                                const isAvailable = isOptionAvailable(
                                    variants,
                                    optionType,
                                    value,
                                    selectedOptions
                                );

                                return (
                                    <button
                                        key={value}
                                        onClick={() => handleOptionSelect(optionType, value)}
                                        disabled={!isAvailable}
                                        className={clsx(
                                            'min-w-[3rem] rounded-lg border px-4 py-2 text-sm font-medium transition-colors',
                                            isSelected
                                                ? 'border-primary-500 bg-primary-50 text-primary-700'
                                                : isAvailable
                                                    ? 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                                                    : 'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed'
                                        )}
                                    >
                                        {value}
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                );
            })}

            {/* Selected Variant Price */}
            {selectedVariant && selectedVariant.price !== '0' && (
                <p className="text-sm text-gray-500">
                    Selected: {selectedVariant.name} (+S${parseFloat(selectedVariant.price).toFixed(2)})
                </p>
            )}
        </div>
    );
}

// Helper functions
function getOptionTypes(variants: ProductVariant[]): string[] {
    const types = new Set<string>();
    variants.forEach((variant) => {
        Object.keys(variant.options).forEach((key) => types.add(key));
    });
    return Array.from(types);
}

function getOptionValues(variants: ProductVariant[], optionType: string): string[] {
    const values = new Set<string>();
    variants.forEach((variant) => {
        if (variant.options[optionType]) {
            values.add(variant.options[optionType]);
        }
    });
    return Array.from(values);
}

function isOptionAvailable(
    variants: ProductVariant[],
    optionType: string,
    value: string,
    currentSelections: Record<string, string>
): boolean {
    return variants.some((variant) => {
        if (variant.options[optionType] !== value) return false;
        if (!variant.isActive) return false;

        // Check if other selected options match
        return Object.entries(currentSelections).every(([key, val]) => {
            if (key === optionType) return true;
            return variant.options[key] === val;
        });
    });
}

export default VariantSelector;
