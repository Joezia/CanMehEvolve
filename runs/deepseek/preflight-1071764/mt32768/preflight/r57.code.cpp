void Decode::ExpandComponents(Field *containingField, const Profile::FIELD_COMPONENT *components, FIT_UINT16 numComponents)
{
    FIT_UINT16 offset = 0;
    const auto mesgNum = mesg.GetNum();

    for (FIT_UINT16 i = 0; i < numComponents; i++)
    {
        const Profile::FIELD_COMPONENT &component = components[i];
        const auto componentBits = component.bits;

        if (component.num != FIT_FIELD_NUM_INVALID)
        {
            const auto componentNum = component.num;
            Field componentField(mesgNum, componentNum);
            FIT_FLOAT64 value;
            FIT_UINT64 bitsValue = FIT_UINT64_INVALID;
            FIT_SINT64 signedBitsValue = FIT_SINT64_INVALID;

            // Mark that this field has been generated through expansion
            componentField.SetIsExpanded(FIT_TRUE);

            const FIT_BOOL isSigned = componentField.IsSignedInteger();
            if (isSigned)
            {
                signedBitsValue = containingField->GetBitsSignedValue64(offset, componentBits);

                if (signedBitsValue == FIT_SINT64_INVALID)
                    break; // No more data for components.

                if (component.accumulate)
                    bitsValue = accumulator.Accumulate(mesgNum, componentNum, signedBitsValue, componentBits);
            }
            else
            {
                bitsValue = containingField->GetBitsValue64(offset, componentBits);

                if (bitsValue == FIT_UINT64_INVALID)
                    break; // No more data for components.

                if (component.accumulate)
                    bitsValue = accumulator.Accumulate(mesgNum, componentNum, bitsValue, componentBits);
            }

            const FIT_UINT16 numComponentsInField = componentField.GetNumComponents();
            const FIT_FLOAT64 componentScale = component.scale;
            const FIT_FLOAT64 componentOffset = component.offset;

            // If the component field itself has *one* component apply the scale and offset of the componentField's
            // (nested) component
            if (numComponentsInField == 1)
            {
                const Profile::FIELD_COMPONENT *nestedComponent = componentField.GetComponent(0);
                if (isSigned)
                    value = (((signedBitsValue / componentScale) - componentOffset) + nestedComponent->offset) * nestedComponent->scale;
                else
                    value = (((bitsValue / componentScale) - componentOffset) + nestedComponent->offset) * nestedComponent->scale;

                fit::Field *currentField = mesg.GetField(componentNum);
                if (currentField)
                {
                    currentField->AddRawValue(value, currentField->GetNumValues());
                }
                else
                {
                    componentField.AddRawValue(value, 0);
                    mesg.AddField(componentField);
                }
            }
            // The component field is itself a composite field (more than one component).  Don't use scale/offset, containing
            // field data must already be encoded.  Add elements to it until we have added bitsvalue
            else if (numComponentsInField > 1)
            {
                if (componentBits > 0)
                {
                    const FIT_UINT8 baseTypeSize = baseTypeSizes[componentField.GetType() & FIT_BASE_TYPE_NUM_MASK];
                    const FIT_UINT64 mask = (static_cast<FIT_UINT64>(1) << baseTypeSize) - 1;
                    int bitsAdded = 0;

                    fit::Field *field = mesg.GetField(componentNum);
                    if (!field)
                    {
                        componentField.AddValue(bitsValue & mask, componentField.GetNumValues());
                        mesg.AddField(componentField);
                        bitsValue >>= baseTypeSize;
                        bitsAdded += baseTypeSize;
                        if (bitsAdded < componentBits)
                            field = mesg.GetField(componentNum);
                    }

                    if (bitsAdded < componentBits)
                    {
                        while (bitsAdded < componentBits)
                        {
                            field->AddValue(bitsValue & mask, field->GetNumValues());
                            bitsValue >>= baseTypeSize;
                            bitsAdded += baseTypeSize;
                        }
                    }
                }
            }
            // componentField is an ordinary field, apply scale and offset as usual
            else
            {
                const FIT_UINT16 subfieldIndex = mesg.GetActiveSubFieldIndex(componentNum);
                if (isSigned)
                    value = (((signedBitsValue / componentScale) - componentOffset) + componentField.GetOffset(subfieldIndex)) * componentField.GetScale(subfieldIndex);
                else
                    value = (((bitsValue / componentScale) - componentOffset) + componentField.GetOffset(subfieldIndex)) * componentField.GetScale(subfieldIndex);

                fit::Field *currentField = mesg.GetField(componentNum);
                if (currentField)
                {
                    currentField->AddRawValue(value, currentField->GetNumValues());
                }
                else
                {
                    componentField.AddRawValue(value, 0);
                    mesg.AddField(componentField);
                }
            }
        }
        offset += componentBits;
    }
}
