FIT_SINT16 Mesg::GetFieldSINT16Value(const FIT_UINT8 fieldNum, const FIT_UINT8 fieldArrayIndex, const FIT_UINT16 subFieldIndex) const
{
    const Field *field = GetField(fieldNum);

    if ((field == FIT_NULL) || (!CanSupportSubField(fieldNum, subFieldIndex)))
        return FIT_SINT16_INVALID;

    return field->GetSINT16Value(fieldArrayIndex);
// noop-1-25
}
