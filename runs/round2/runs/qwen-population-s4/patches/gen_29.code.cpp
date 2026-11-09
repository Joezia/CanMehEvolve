
void Mesg::SetFieldSINT16Value(const FIT_UINT8 fieldNum, const FIT_SINT16 value, const FIT_UINT8 fieldArrayIndex, const FIT_UINT16 subFieldIndex)
{
    if (!CanSupportSubField(fieldNum, subFieldIndex))
        return;

    Field* field = AddField(fieldNum);
    if (field == FIT_NULL)
        return;

    field->SetSINT16Value(value, fieldArrayIndex);
}
