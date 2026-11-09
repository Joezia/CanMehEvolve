Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    Field* const p = fields.data();
    const int n = (int)fields.size();
    int i = 0;

    for (; n - i >= 4; i += 4)
    {
        if (p[i].GetNum() == fieldNum) return &p[i];
        if (p[i + 1].GetNum() == fieldNum) return &p[i + 1];
        if (p[i + 2].GetNum() == fieldNum) return &p[i + 2];
        if (p[i + 3].GetNum() == fieldNum) return &p[i + 3];
    }

    for (; i < n; ++i)
    {
        if (p[i].GetNum() == fieldNum)
            return &p[i];
    }

    return FIT_NULL;
}
