FIT_UINT8 Field::GetNum(void) const
{
    const fit::Profile* p = profile;
    if ((p == NULL) || (profileIndex >= p->numFields))
        return FIT_FIELD_NUM_INVALID;
    return p->fields[profileIndex].num;
}
