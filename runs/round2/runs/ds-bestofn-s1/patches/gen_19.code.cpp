FIT_UINT8 Field::GetNum(void) const
{
    const auto* p = profile;
    const auto index = profileIndex;
    if (__builtin_expect((p == NULL) || (index >= p->numFields), 0))
        return FIT_FIELD_NUM_INVALID;
    return p->fields[index].num;
}
