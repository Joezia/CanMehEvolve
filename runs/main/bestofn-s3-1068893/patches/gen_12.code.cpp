const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    const FIELD *field = mesg->fields;
    const FIELD *field_end = field + mesg->numFields;

    while (field < field_end)
    {
        if (field->num == fieldNum)
            return static_cast<FIT_UINT16>(field - mesg->fields);
        field++;
    }

    return FIT_UINT16_INVALID;
}
