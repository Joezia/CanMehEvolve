FIT_BOOL Mesg::HasField(const int fieldNum) const
{
    const Field* p = fields.data();
    auto n = fields.size();

    if (n & 1)
    {
        if (p->GetNum() == fieldNum)
            return FIT_TRUE;
        ++p;
    }

    if (n & 2)
    {
        if (p->GetNum() == fieldNum)
            return FIT_TRUE;
        ++p;
        if (p->GetNum() == fieldNum)
            return FIT_TRUE;
        ++p;
    }

    n >>= 2;

    while (n != 0)
    {
        if (p[0].GetNum() == fieldNum) return FIT_TRUE;
        if (p[1].GetNum() == fieldNum) return FIT_TRUE;
        if (p[2].GetNum() == fieldNum) return FIT_TRUE;
        if (p[3].GetNum() == fieldNum) return FIT_TRUE;
        p += 4;
        --n;
    }

    return FIT_FALSE;
}
