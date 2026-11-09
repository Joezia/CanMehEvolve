void Decode::ExpandComponents(Field *containingField, const Profile::FIELD_COMPONENT *components, FIT_UINT16 numComponents)
{
    FIT_UINT16 offset = 0;
    const FIT_MESG_NUM mesgNum = mesg.GetNum();

    for (FIT_UINT16 i = 0; i < numComponents; ++i)
    {
        const Profile::FIELD_COMPONENT *component = &components[i];
        const FIT_FIELD_NUM fieldNum = component->num;
        const FIT_UINT8 bits = component->bits;

        if (fieldNum != FIT_FIELD_NUM_INVALID)
        {
            Field componentField(mesgNum, fieldNum);
            const FIT_BOOL isSigned = componentField.IsSignedInteger();
            FIT_FLOAT64 value;
            FIT_UINT64 bitsValue = FIT_UINT64_INVALID;
            FIT_SINT64 signedBitsValue = FIT_SINT64_INVALID;

            if (isSigned)
            {
                signedBitsValue = containingField->GetBitsSignedValue64(offset, bits);

                if (signedBitsValue == FIT_SINT64_INVALID)
                    break; // No more data for components.

                if (component->accumulate)
                    bitsValue = accumulator.Accumulate(mesgNum, fieldNum, signedBitsValue, bits);
            }
            else
            {
                bitsValue = containingField->GetBitsValue64(offset, bits);

                if (bitsValue == FIT_UINT64_INVALID)
                    break; // No more data for components.

                if (component->accumulate)
                    bitsValue = accumulator.Accumulate(mesgNum, fieldNum, bitsValue, bits);
            }

            const FIT_UINT16 numFieldComponents = componentField.GetNumComponents();
            Field *currentField = mesg.GetField(fieldNum);

            if (numFieldComponents == 1)
            {
                const Profile::FIELD_COMPONENT *nested = componentField.GetComponent(0);

                if (isSigned)
                    value = (((signedBitsValue / (FIT_FLOAT64)component->scale) - component->offset) + nested->offset) * nested->scale;
                else
                    value = (((bitsValue / (FIT_FLOAT64)component->scale) - component->offset) + nested->offset) * nested->scale;

                if (currentField)
                {
                    currentField->AddRawValue(value, currentField->GetNumValues());
                }
                else
                {
                    componentField.SetIsExpanded(FIT_TRUE);
                    componentField.AddRawValue(value, 0);
                    mesg.AddField(componentField);
                }
            }
            else if (numFieldComponents > 1)
            {
                const FIT_UINT8 baseTypeSize = baseTypeSizes[componentField.GetType() & FIT_BASE_TYPE_NUM_MASK];
                const FIT_UINT64 mask = ((FIT_UINT64)1 << baseTypeSize) - 1;
                int bitsAdded = 0;

                while (bitsAdded < bits)
                {
                    if (currentField)
                    {
                        currentField->AddValue(bitsValue & mask, currentField->GetNumValues());
                    }
                    else
                    {
                        componentField.SetIsExpanded(FIT_TRUE);
                        componentField.AddValue(bitsValue & mask, 0);
                        mesg.AddField(componentField);
                        currentField = mesg.GetField(fieldNum);
                    }

                    bitsValue >>= baseTypeSize;
                    bitsAdded += baseTypeSize;
                }
            }
            else
            {
                const FIT_UINT16 subfieldIndex = mesg.GetActiveSubFieldIndex(fieldNum);

                if (isSigned)
                    value = (((signedBitsValue / (FIT_FLOAT64)component->scale) - component->offset) + componentField.GetOffset(subfieldIndex)) * componentField.GetScale(subfieldIndex);
                else
                    value = (((bitsValue / (FIT_FLOAT64)component->scale) - component->offset) + componentField.GetOffset(subfieldIndex)) * componentField.GetScale(subfieldIndex);

                if (currentField)
                {
                    currentField->AddRawValue(value, currentField->GetNumValues());
                }
                else
                {
                    componentField.SetIsExpanded(FIT_TRUE);
                    componentField.AddRawValue(value, 0);
                    mesg.AddField(componentField);
                }
            }
        }

        offset += bits;
    }
}
