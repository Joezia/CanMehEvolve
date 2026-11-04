
void Decode::ExpandComponents(Field *containingField, const Profile::FIELD_COMPONENT *components, FIT_UINT16 numComponents)
{
    FIT_UINT16 offset = 0;

    for (FIT_UINT16 i = 0; i < numComponents; i++)
    {
        const Profile::FIELD_COMPONENT *component = &components[i];

        if (component->num == FIT_FIELD_NUM_INVALID)
            continue;

        Field componentField(mesg.GetNum(), component->num);
        FIT_UINT16 subfieldIndex = mesg.GetActiveSubFieldIndex(componentField.GetNum());
        FIT_FLOAT64 value;
        FIT_UINT64 bitsValue = FIT_UINT64_INVALID;
        FIT_SINT64 signedBitsValue = FIT_SINT64_INVALID;

        componentField.SetIsExpanded(FIT_TRUE);

        if (componentField.IsSignedInteger())
        {
            signedBitsValue = containingField->GetBitsSignedValue64(offset, component->bits);
            if (signedBitsValue == FIT_SINT64_INVALID)
                break;
            if (component->accumulate)
                bitsValue = accumulator.Accumulate(mesg.GetNum(), component->num, signedBitsValue, component->bits);
        }
        else
        {
            bitsValue = containingField->GetBitsValue64(offset, component->bits);
            if (bitsValue == FIT_UINT64_INVALID)
                break;
            if (component->accumulate)
                bitsValue = accumulator.Accumulate(mesg.GetNum(), component->num, bitsValue, component->bits);
        }

        // Use reference to avoid repeated lookups
        const Profile::FIELD_COMPONENT *nestedComponent = componentField.GetNumComponents() == 1 ? componentField.GetComponent(0) : nullptr;

        if (nestedComponent)
        {
            if (componentField.IsSignedInteger())
                value = (((signedBitsValue / (FIT_FLOAT64)component->scale) - component->offset) + nestedComponent->offset) * nestedComponent->scale;
            else
                value = (((bitsValue / (FIT_FLOAT64)component->scale) - component->offset) + nestedComponent->offset) * nestedComponent->scale;
        }
        else if (componentField.GetNumComponents() > 1)
        {
            const FIT_UINT8 type = componentField.GetType() & FIT_BASE_TYPE_NUM_MASK;
            const FIT_UINT8 baseSize = baseTypeSizes[type];
            const FIT_UINT64 mask = ((FIT_UINT64)1 << baseSize) - 1;

            int bitsAdded = 0;
            while (bitsAdded < component->bits)
            {
                if (mesg.HasField(componentField.GetNum()))
                {
                    Field *field = mesg.GetField(componentField.GetNum());
                    field->AddValue(bitsValue & mask, field->GetNumValues());
                }
                else
                {
                    componentField.AddValue(bitsValue & mask, componentField.GetNumValues());
                    mesg.AddField(componentField);
                }
                bitsValue >>= baseSize;
                bitsAdded += baseSize;
            }
            continue;
        }
        else
        {
            if (componentField.IsSignedInteger())
                value = (((signedBitsValue / (FIT_FLOAT64)component->scale) - component->offset) + componentField.GetOffset(subfieldIndex)) * componentField.GetScale(subfieldIndex);
            else
                value = (((bitsValue / (FIT_FLOAT64)component->scale) - component->offset) + componentField.GetOffset(subfieldIndex)) * componentField.GetScale(subfieldIndex);
        }

        if (mesg.HasField(componentField.GetNum()))
        {
            Field *currentField = mesg.GetField(componentField.GetNum());
            currentField->AddRawValue(value, currentField->GetNumValues());
        }
        else
        {
            componentField.AddRawValue(value, componentField.GetNumValues());
            mesg.AddField(componentField);
        }

        offset += component->bits;
    }
}
