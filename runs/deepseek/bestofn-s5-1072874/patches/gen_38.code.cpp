FIT_UINT8 Field::GetType() const
{
    if (__builtin_expect(type == FIT_UINT8_INVALID, 0))
    {
        if ((profile == NULL) || (profileIndex >= profile->numFields))
            return FIT_UINT8_INVALID;

        return profile->fields[profileIndex].type;
    }

    return type;
}
