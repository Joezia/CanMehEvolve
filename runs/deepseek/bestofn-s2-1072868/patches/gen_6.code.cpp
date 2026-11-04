FIT_FLOAT64 FieldBase::GetOffset(const FIT_UINT16 subFieldIndex) const
{
    if (subFieldIndex < numSubFields)
    {
        const SubFieldBase* subfield = subFields[subFieldIndex];
        return NULL != subfield ? subfield->offset : 0.0;
    }

    return offset;
}
