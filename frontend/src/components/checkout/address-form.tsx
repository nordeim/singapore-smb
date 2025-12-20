/**
 * Address Form Component
 * 
 * Shipping address form with Singapore validation.
 */
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import type { AddressFormData } from '@/types';

const addressSchema = z.object({
    recipientName: z.string().min(1, 'Recipient name is required'),
    phone: z
        .string()
        .min(1, 'Phone number is required')
        .regex(/^(\+65)?[689]\d{7}$/, 'Please enter a valid Singapore phone number'),
    addressLine1: z.string().min(1, 'Address is required'),
    addressLine2: z.string().optional(),
    postalCode: z
        .string()
        .min(1, 'Postal code is required')
        .regex(/^\d{6}$/, 'Postal code must be 6 digits'),
    unitNumber: z.string().optional(),
    saveAsDefault: z.boolean().optional(),
});

interface AddressFormProps {
    onSubmit: (data: AddressFormData) => void;
    defaultValues?: Partial<AddressFormData>;
}

export function AddressForm({ onSubmit, defaultValues }: AddressFormProps) {
    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<AddressFormData>({
        resolver: zodResolver(addressSchema),
        defaultValues: {
            recipientName: defaultValues?.recipientName || '',
            phone: defaultValues?.phone || '',
            addressLine1: defaultValues?.addressLine1 || '',
            addressLine2: defaultValues?.addressLine2 || '',
            postalCode: defaultValues?.postalCode || '',
            unitNumber: defaultValues?.unitNumber || '',
            saveAsDefault: defaultValues?.saveAsDefault || false,
        },
    });

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Recipient Name */}
            <Input
                label="Recipient Name"
                placeholder="John Doe"
                error={errors.recipientName?.message}
                {...register('recipientName')}
            />

            {/* Phone */}
            <Input
                label="Phone Number"
                type="tel"
                placeholder="+65 9123 4567"
                helpText="Singapore mobile or landline"
                error={errors.phone?.message}
                {...register('phone')}
            />

            {/* Address Line 1 */}
            <Input
                label="Address"
                placeholder="Block 123 Street Name"
                error={errors.addressLine1?.message}
                {...register('addressLine1')}
            />

            {/* Address Line 2 */}
            <Input
                label="Address Line 2"
                placeholder="Building name (optional)"
                error={errors.addressLine2?.message}
                {...register('addressLine2')}
            />

            {/* Postal Code & Unit Number */}
            <div className="grid gap-4 sm:grid-cols-2">
                <Input
                    label="Postal Code"
                    placeholder="123456"
                    maxLength={6}
                    error={errors.postalCode?.message}
                    {...register('postalCode')}
                />
                <Input
                    label="Unit Number"
                    placeholder="#01-23"
                    error={errors.unitNumber?.message}
                    {...register('unitNumber')}
                />
            </div>

            {/* Save as Default */}
            <label className="flex items-center gap-2">
                <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    {...register('saveAsDefault')}
                />
                <span className="text-sm text-gray-600">Save as default address</span>
            </label>

            {/* Submit */}
            <Button type="submit" loading={isSubmitting} className="w-full">
                Continue to Payment
            </Button>
        </form>
    );
}

export default AddressForm;
