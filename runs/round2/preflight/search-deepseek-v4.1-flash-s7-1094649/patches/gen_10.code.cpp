FIT_UINT8 Field::GetNum(void) const
{
    const Profile::MESG *p = profile;
    if (p == NULL)
        return FIT_FIELD_NUM_INVALID;
    const FIT_UINT8 i = profileIndex;
    if (i >= p->numFields)
        return FIT_FIELD_NUM_INVALID;
    return p->fields[i].num;
}
