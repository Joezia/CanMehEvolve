
const Profile::FIELD* Profile::GetField(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == NULL)
        return NULL;

    // Binary search since fields are sorted by field number
    const FIELD* begin = mesg->fields;
    const FIELD* end = mesg->fields + mesg->numFields;
    const FIELD* it = std::lower_bound(begin, end, fieldNum,
        [](const FIELD& a, FIT_UINT8 val) { return a.fieldNum < val; });

    if (it == end || it->fieldNum != fieldNum)
        return NULL;

    return it;
}
