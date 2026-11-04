FIT_UINT8 Mesg::GetFieldUINT8Value(const FIT_UINT8 fieldNum, const FIT_UINT8 fieldArrayIndex, const FIT_UINT16 subFieldIndex) const
{
    const Field *field = GetField(fieldNum);

    if (field == FIT_NULL)
        return FIT_UINT8_INVALID;

    if ((subFieldIndex != FIT_SUBFIELD_INDEX_MAIN_FIELD) && (!field->CanSupportSubField(subFieldIndex)))
        return FIT_UINT8_INVALID;

    return field->GetUINT8Value(fieldArrayIndex);
}
