FIT_UINT8 Field::GetType() const
{
    FIT_UINT8 result = type;

    if (__builtin_expect(result == FIT_UINT8_INVALID, 0))
    {
        const Profile* p = profile;
        if ((p != NULL) && (profileIndex < p->numFields))
            result = p->fields[profileIndex].type;
    }

    return result;
}
