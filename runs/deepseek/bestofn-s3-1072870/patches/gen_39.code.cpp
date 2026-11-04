Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    Field* p = fields.data();
    const size_t n = fields.size();

    for (size_t i = 0; i < n; ++i)
    {
        if (p[i].GetNum() == fieldNum)
            return p + i;
    }

    return FIT_NULL;
}
