
const Profile::FIELD* Profile::GetField(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == nullptr)
        return nullptr;

    // Use binary search since fields are stored sorted by fieldNum per message
    const FIELD key = { 0, 0, fieldNum };
    const FIELD* begin = mesg->fields;
    const FIELD* end = mesg->fields + mesg->numFields;
    const FIELD* it = std::lower_bound(begin, end, key,
        [](const FIELD& a, const FIELD& b) { return a.fieldNum < b.fieldNum; });

    if (it == end || it->fieldNum != fieldNum)
        return nullptr;

    return it;
}
