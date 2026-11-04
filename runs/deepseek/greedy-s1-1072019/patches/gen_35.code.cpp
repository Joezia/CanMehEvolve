FIT_UINT8 Field::GetNum(void) const
{
    const auto *p = profile;
    const auto index = profileIndex;
    if (p == NULL)
        return FIT_FIELD_NUM_INVALID;
    const auto *fields = p->fields;
    if (index >= p->numFields)
        return FIT_FIELD_NUM_INVALID;
    return fields[index].num;
}
