const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    struct Lut {
        const Profile::MESG* p[65536] = {};
        Lut()
        {
            for (int i = MESGS - 1; i >= 0; --i)
                p[mesgs[i].num] = &mesgs[i];
        }
    };
    static const Lut lut;
    return lut.p[num];
}
