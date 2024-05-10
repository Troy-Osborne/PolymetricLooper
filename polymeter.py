from math import sin,cos,pi
from struct import pack
tau=pi*2
class Polymeter():
    def __init__(self,Patterns=[[3,{0:0}],
                                [4,{0:1,2:2,3:3}],
                                [5,{0:4,3:5,4:6}]]):
        self.Patterns=Patterns
        
    def makebars(self,start,end):
        notes=[]
        for Layer in self.Patterns:
            Length=Layer[0]
            NL=NoteLength(Length)*1000
            for step in range(start,end):
                pos=step%Length
                if pos in Layer[1]:
                    notes.append((step,Layer[1][pos],NL))
        return notes

def BlipEnv(Length=3000):
    A=int(44100/1000*15)
    R=int(44100/1000*(Length-15))
    o=[]
    for i in range(A):#15 milliseconds
        o.append(i/A)
    for i in range(R):
        o.append(1-i/R)
    return o

def Blip(n,tuning,Length=1000):
    freq=tuning*2**(n/12)###By Default everything will be tuned to 0= A0 you'll have to add the semitones after -49 to change it
    #e.g. 440*2**((Nums[n]-49+2)/12) would tune it to B or 440*2**((Nums[n]-49+3)/12) to C
    env=BlipEnv(Length)
    return [int((sin(freq/44100*i*tau)*env[i]/((1+n/12)**2))*2**12) for i in range(len(env))]
                

def NaturalPolymeter(Notes,Octaves=4,Direction="UpBounce",Depth=64,offset=lambda Len:0):
    #Directions:
    #Up starts at bottom going up then repeats at bottom
    #Down starts at top going down then repeats at top
    #UpBounce starts at bottom going up top to bottom, then repeat
    #Down starts at top going down then goes up to top, then repeat
    ln=len(Notes)*Octaves
    out=[]
    N=0 if Direction=="UpBounce" or Direction=="Up" else ln-1
    currentdir=1 if Direction=="UpBounce" or Direction=="Up" else -1
    for i in range(Depth):
        Length=1+i
        notenum=Notes[N%len(Notes)]+12*(N//len(Notes))
        out.append([Length,{offset(Length):notenum}])
        N+=currentdir

        if currentdir==1 and N>=ln:
            currentdir=1 if Direction=="Up" else -1
            N=0 if Direction=="Up" else N-2
        if currentdir==-1 and N<0:
            currentdir=-1 if Direction=="Down" else 1
            N=ln-1 if Direction=="Down" else N+2
    return out
            
TotalLen=1024     
StepsPerSecond=5
NoteLength=lambda patternlength:patternlength/16  #in milliseconds


Patterns=NaturalPolymeter([0,3,7,10,14],Octaves=5,Depth=96,offset=lambda Len:Len-1)#96 layers, G minor 9 chord repeating across 5 octaves, offset is set to play each note in the last step of its pattern.
P=Polymeter(Patterns)#Create polymeter instance from the patterns
notes=P.makebars(0,TotalLen) #create notes from the polymeter instance


def SongFromNotes(Notes,StepsPerSecond=1,Tuning=98,Steps=TotalLen):
    import wave
    CurrentNotes=[]#notenum and pos
    FrameCount=(Steps*44100)//StepsPerSecond
    Outlist=[0 for i in range(FrameCount)]
    for note in Notes:
        notepos,notenum,notelen=note
        Sound=Blip(notenum,Tuning,max(notelen,2000))
        curpos=(notepos*44100)//StepsPerSecond
        for val in Sound:
            if curpos>=FrameCount:
                break
            Outlist[curpos]+=val
            curpos+=1
    return Outlist
    

def savesound(l,name="polymeterLogVol.wav"):
    import wave
    f=wave.open(name,"w")
    f.setframerate(44100)
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setnframes(len(l))
    for val in l:
        val=-32768 if val<-32768  else val
        val=32767 if val>32767  else val
        f.writeframes(pack("h",val))
    return f
        
SongWav=SongFromNotes(notes,StepsPerSecond,98,TotalLen)#Turn Notes into PCM16
outfile=savesound(SongWav)#Export Wave
outfile.close()
